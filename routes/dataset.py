"""LoanWise AI - dataset management routes.

THE CORE FLOW (read this before changing anything):
  1. User uploads a CSV manually on this page (drag-drop or Browse).
     Nothing is bundled, nothing is auto-loaded, nothing trains on
     file-select. Upload only validates + stores + summarises.
  2. The page shows the real summary cards and a searchable,
     paginated preview of the actual uploaded rows.
  3. ONLY when the user clicks "Process Dataset & Train Models" does
     training happen. On success the new dataset becomes the active
     one and the previous active dataset is marked 'replaced' - the
     old models are swapped only after the new training succeeds, and
     all previous predictions are kept.
"""
import json
import os
from datetime import datetime

import pandas as pd
from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from werkzeug.utils import secure_filename

from database.db import Dataset, db
from ml.evaluation import build_all_charts
from ml.preprocessing import (FEATURE_LABELS, REQUIRED_COLUMNS,
                              clean_dataframe, summarise, validate_csv)
from ml.training import train_all
from routes.common import active_dataset, current_user, login_required

dataset_bp = Blueprint("dataset", __name__)
ALLOWED_EXTENSIONS = {"csv"}
PER_PAGE = 10


def _allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _read_csv(filepath):
    df = pd.read_csv(filepath)
    return clean_dataframe(df)


@dataset_bp.route("/dataset")
@login_required
def dataset_page():
    """Dataset Management page: latest upload + preview + version list."""
    latest = Dataset.query.order_by(Dataset.created_at.desc()).first()
    active = active_dataset()
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "").strip()
    preview_rows, total_preview, columns = [], 0, []
    summary = None
    if latest is not None:
        try:
            df = _read_csv(latest.filepath)
            summary = summarise(df)
            columns = list(df.columns)
            if search:
                mask = df.astype(str).apply(
                    lambda row: row.str.contains(search, case=False, na=False)
                ).any(axis=1)
                df = df[mask]
            total_preview = len(df)
            start = (page - 1) * PER_PAGE
            preview_rows = df.iloc[start:start + PER_PAGE].to_dict("records")
        except Exception as exc:  # file unreadable -> show the error, don't crash
            flash(f"Could not read the uploaded file: {exc}", "error")
    pages = max(1, (total_preview + PER_PAGE - 1) // PER_PAGE)
    versions = Dataset.query.order_by(Dataset.created_at.desc()).all()
    return render_template(
        "dataset.html",
        user=current_user(),
        dataset=latest,
        active=active,
        summary=summary,
        columns=columns,
        rows=preview_rows,
        page=page,
        pages=pages,
        search=search,
        total_preview=total_preview,
        versions=versions,
    )


@dataset_bp.route("/dataset/upload", methods=["POST"])
@login_required
def upload():
    """Step 1 - manual upload. Validates and stores only; NO training here."""
    file = request.files.get("csv_file")
    if file is None or file.filename == "":
        flash("Please choose a CSV file first.", "error")
        return redirect(url_for("dataset.dataset_page"))
    if not _allowed(file.filename):
        flash("Only CSV files are supported.", "error")
        return redirect(url_for("dataset.dataset_page"))

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stored = f"{stamp}_{secure_filename(file.filename)}"
    filepath = os.path.join(upload_dir, stored)
    file.save(filepath)

    try:
        df = _read_csv(filepath)
    except Exception as exc:
        os.remove(filepath)
        flash(f"Could not read this CSV file: {exc}", "error")
        return redirect(url_for("dataset.dataset_page"))

    errors = validate_csv(df)
    if errors:
        os.remove(filepath)
        for err in errors:
            flash(err, "error")
        return redirect(url_for("dataset.dataset_page"))
    if df.isna().sum().sum() > 0:
        # Spec: validate missing values. We warn and refuse - the
        # reference dataset has zero missing values, and training on
        # rows with missing values would silently change results.
        os.remove(filepath)
        flash("The CSV contains missing values. Please upload a complete dataset.", "error")
        return redirect(url_for("dataset.dataset_page"))

    summary = summarise(df)
    ds = Dataset(
        original_filename=file.filename,
        stored_filename=stored,
        filepath=filepath,
        total_rows=summary["total_rows"],
        total_columns=summary["total_columns"],
        missing_values=summary["missing_values"],
        duplicate_rows=summary["duplicate_rows"],
        approved=summary["approved"],
        rejected=summary["rejected"],
        status="uploaded",
    )
    db.session.add(ds)
    db.session.commit()
    flash(
        f"Dataset uploaded: {summary['total_rows']:,} rows, "
        f"{summary['total_columns']} columns, {summary['approved']:,} Approved / "
        f"{summary['rejected']:,} Rejected. Click 'Process Dataset & Train Models' to train.",
        "success",
    )
    return redirect(url_for("dataset.dataset_page"))


@dataset_bp.route("/dataset/process/<int:dataset_id>", methods=["POST"])
@login_required
def process(dataset_id):
    """Step 2 - training. Runs ONLY when the user clicks the button."""
    ds = Dataset.query.get_or_404(dataset_id)
    if ds.status == "trained" and ds.is_active:
        flash("This dataset is already trained and active.", "success")
        return redirect(url_for("dataset.dataset_page"))
    previous_active = active_dataset()
    if previous_active is not None and previous_active.id != ds.id:
        # Explicit replacement confirmation (spec section 5I).
        if not request.form.get("confirm_replace"):
            flash("Tick 'I understand this will replace the active dataset' to confirm replacement.", "error")
            return redirect(url_for("dataset.dataset_page"))

    ds.status = "training"
    ds.error_message = None
    db.session.commit()
    try:
        df = _read_csv(ds.filepath)
        errors = validate_csv(df)
        if errors:
            raise ValueError("; ".join(errors))
        model_dir = os.path.join(current_app.config["MODEL_FOLDER"], f"dataset_{ds.id}")
        models, metrics, split, importances, best_name, _y_test, _y_pred = train_all(df, model_dir)
        chart_dir = current_app.config["CHART_FOLDER"]
        build_all_charts(metrics, best_name, importances, FEATURE_LABELS, chart_dir)
    except Exception as exc:
        ds.status = "failed"
        ds.error_message = str(exc)
        db.session.commit()
        flash(f"Training failed: {exc}", "error")
        return redirect(url_for("dataset.dataset_page"))

    # Success only: swap the active dataset. Old predictions are kept.
    if previous_active is not None and previous_active.id != ds.id:
        previous_active.status = "replaced"
        previous_active.is_active = False
    ds.status = "trained"
    ds.is_active = True
    ds.train_count = split["train"]
    ds.test_count = split["test"]
    # Store metrics without the 1,281 raw test predictions (kept in memory only).
    ds.metrics_json = json.dumps({
        name: {k: v for k, v in m.items() if k != "y_pred"}
        for name, m in metrics.items()
    })
    ds.trained_at = datetime.utcnow()
    db.session.commit()
    flash(
        f"Training complete. Best model: {best_name} "
        f"({metrics[best_name]['accuracy'] * 100:.2f}% accuracy). "
        f"Train {split['train']:,} / Test {split['test']:,} records.",
        "success",
    )
    return redirect(url_for("dataset.performance"))


@dataset_bp.route("/performance")
@login_required
def performance():
    """Model Performance page - real metrics from the active dataset only."""
    ds = active_dataset()
    metrics = None
    best_model = None
    importances = None
    if ds is not None and ds.metrics_json:
        metrics = json.loads(ds.metrics_json)
        best_model = max(metrics, key=lambda n: (metrics[n]["accuracy"], metrics[n]["f1"]))
        # Feature importances are read back from the saved Random Forest.
        try:
            import joblib
            rf = joblib.load(os.path.join(
                current_app.config["MODEL_FOLDER"], f"dataset_{ds.id}", "random_forest.joblib"))
            from ml.preprocessing import FEATURE_COLUMNS
            importances = {
                FEATURE_LABELS.get(col, col): float(v)
                for col, v in zip(FEATURE_COLUMNS, rf.named_steps["model"].feature_importances_)
            }
            importances = dict(sorted(importances.items(), key=lambda kv: kv[1], reverse=True))
        except Exception:
            importances = None
    return render_template(
        "performance.html",
        user=current_user(),
        dataset=ds,
        metrics=metrics,
        best_model=best_model,
        importances=importances,
    )
