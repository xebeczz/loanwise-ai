"""LoanWise AI - Render-only auto-seed.

WHY THIS EXISTS
---------------
Render's free web service has an ephemeral disk: every restart or
redeploy wipes loanwise.db, the uploaded CSVs and the trained models.
The app itself never deletes anything - the host does. That wiped the
live demo twice in two days (2026-11-13 and 2026-11-14), so the demo
account stopped logging in and the dashboard went empty again.

WHAT IT DOES
------------
On Render ONLY (never on a local run), at app startup, if the database
has no dataset at all, this module restores the demo by itself:

  1. Copies the bundled demo CSV (data/demo_dataset.csv - the same
     Kaggle Loan Approval Prediction Dataset, 4,269 rows) into the
     upload folder, exactly as if it had been uploaded.
  2. Trains the same five models with the same train_all() used by
     "Process Dataset & Train Models" (70/30 split, random_state=42).
  3. Marks that dataset trained + active, builds the charts.
  4. Creates the demo account retrain@loanwise.ai / Retrain1234!
     (the login already given to Hakeem) if it does not exist.

After a wipe the first boot takes ~20 seconds longer, then the live
link works again by itself - nobody has to re-register, re-upload or
re-train by hand.

WHAT IT DOES NOT DO
------------------
- It NEVER runs locally (python app.py on a laptop): local runs stay
  manual-upload-only, exactly as the college spec requires. The
  trigger is the Render environment (RENDER env var set by Render,
  or FLASK_ENV=production, which render.yaml sets).
- It NEVER runs if any dataset row already exists: if Hakeem (or a
  user) has uploaded a CSV, even an untrained one, the seed leaves it
  alone and never hijacks it.
- It NEVER changes an existing trained dataset, and it never deletes
  predictions or users.
- Set LOANWISE_AUTO_SEED=0 to switch it off entirely.

It never crashes startup: any failure is logged and the app still
starts (empty, manual flow as before).
"""
import json
import os
import shutil
from datetime import datetime

import pandas as pd
from werkzeug.security import generate_password_hash

DEMO_EMAIL = "retrain@loanwise.ai"
DEMO_PASSWORD = "Retrain1234!"
DEMO_NAME = "Demo User"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DEMO_CSV = os.path.join(BASE_DIR, "data", "demo_dataset.csv")


def _auto_seed_enabled():
    """Render-only. Explicit LOANWISE_AUTO_SEED=0 disables it anywhere."""
    if os.environ.get("LOANWISE_AUTO_SEED", "").strip() == "0":
        return False
    return "RENDER" in os.environ or os.environ.get("FLASK_ENV") == "production"


def seed_demo_if_needed(app):
    """Restore the demo dataset + demo account after a Render wipe.

    Returns True when it seeded, False when it skipped or failed.
    Never raises - a failed seed must not stop the app from starting.
    """
    if not _auto_seed_enabled():
        return False
    try:
        with app.app_context():
            from database.db import Dataset, User, db
            from ml.evaluation import build_all_charts
            from ml.preprocessing import (FEATURE_LABELS, clean_dataframe,
                                          summarise, validate_csv)
            from ml.training import train_all

            # Already trained? Leave it alone.
            if Dataset.query.filter_by(is_active=True, status="trained").first():
                return False
            # A user upload exists (trained, failed or waiting)? Never hijack it.
            if Dataset.query.count() > 0:
                app.logger.info("Auto-seed skipped: a dataset already exists.")
                return False
            if not os.path.exists(DEMO_CSV):
                app.logger.warning("Auto-seed skipped: %s not found.", DEMO_CSV)
                return False

            app.logger.info("Auto-seed: restoring demo dataset after a fresh/empty database.")
            upload_dir = app.config["UPLOAD_FOLDER"]
            os.makedirs(upload_dir, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stored = f"{stamp}_loan_approval_dataset.csv"
            filepath = os.path.join(upload_dir, stored)
            shutil.copyfile(DEMO_CSV, filepath)

            df = clean_dataframe(pd.read_csv(filepath))
            errors = validate_csv(df)
            if errors:
                raise ValueError("; ".join(errors))
            if df.isna().sum().sum() > 0:
                raise ValueError("Demo dataset contains missing values.")

            summary = summarise(df)
            ds = Dataset(
                original_filename="loan_approval_dataset.csv",
                stored_filename=stored,
                filepath=filepath,
                total_rows=summary["total_rows"],
                total_columns=summary["total_columns"],
                missing_values=summary["missing_values"],
                duplicate_rows=summary["duplicate_rows"],
                approved=summary["approved"],
                rejected=summary["rejected"],
                status="training",
            )
            db.session.add(ds)
            db.session.commit()

            # Same training path as the manual "Process" button.
            model_dir = os.path.join(app.config["MODEL_FOLDER"], f"dataset_{ds.id}")
            models, metrics, split, importances, best_name, _y_test, _y_pred = train_all(
                df, model_dir
            )
            build_all_charts(
                metrics, best_name, importances, FEATURE_LABELS,
                app.config["CHART_FOLDER"],
            )
            ds.status = "trained"
            ds.is_active = True
            ds.train_count = split["train"]
            ds.test_count = split["test"]
            ds.metrics_json = json.dumps({
                name: {k: v for k, v in m.items() if k != "y_pred"}
                for name, m in metrics.items()
            })
            ds.trained_at = datetime.utcnow()

            if not User.query.filter_by(email=DEMO_EMAIL).first():
                db.session.add(User(
                    name=DEMO_NAME, email=DEMO_EMAIL,
                    password_hash=generate_password_hash(DEMO_PASSWORD),
                ))
            db.session.commit()
            app.logger.info(
                "Auto-seed done: best model %s (%.2f%%), train %d / test %d, demo user %s.",
                best_name, metrics[best_name]["accuracy"] * 100,
                split["train"], split["test"], DEMO_EMAIL,
            )
            return True
    except Exception as exc:  # never stop the app from starting
        try:
            app.logger.error("Auto-seed failed (manual flow still works): %s", exc)
        except Exception:
            print(f"Auto-seed failed (manual flow still works): {exc}")
        return False
