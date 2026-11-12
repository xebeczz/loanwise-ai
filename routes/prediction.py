"""LoanWise AI - prediction routes (New Prediction, Result, History).

Prediction is blocked until a dataset has been uploaded AND trained -
the spec message is shown verbatim in that case. Every prediction is
saved to SQLite so History survives an app restart.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from database.db import Prediction, db
from ml.prediction import predict_all
from routes.common import (active_dataset, current_user, load_active_models,
                           login_required)

prediction_bp = Blueprint("prediction", __name__)

SAMPLE_APPLICANT = {
    "no_of_dependents": 0,
    "education": "Graduate",
    "self_employed": "Salaried",
    "income_annum": 4000000,
    "loan_amount": 11500000,
    "loan_term": 8,
    "cibil_score": 434,
    "residential_assets_value": 4500000,
    "commercial_assets_value": 2800000,
    "luxury_assets_value": 8400000,
    "bank_asset_value": 5900000,
}
BLOCK_MESSAGE = "Please upload and process a loan dataset before making predictions."


def _validate_form(form):
    """Server-side validation (the form also validates in the browser)."""
    errors = []
    try:
        dep = int(form.get("no_of_dependents", ""))
        if dep < 0:
            errors.append("Number of dependents cannot be negative.")
        income = float(form.get("income_annum", ""))
        if income <= 0:
            errors.append("Annual income must be positive.")
        loan = float(form.get("loan_amount", ""))
        if loan <= 0:
            errors.append("Loan amount must be positive.")
        term = int(form.get("loan_term", ""))
        if term <= 0:
            errors.append("Loan term must be positive.")
        cibil = int(form.get("cibil_score", ""))
        if not 300 <= cibil <= 900:
            errors.append("CIBIL score must be between 300 and 900.")
        for field in ("residential_assets_value", "commercial_assets_value",
                      "luxury_assets_value", "bank_asset_value"):
            if float(form.get(field, "")) < 0:
                errors.append("Asset values cannot be negative.")
    except (TypeError, ValueError):
        errors.append("All fields are required and must be valid numbers.")
    return errors


@prediction_bp.route("/prediction/new", methods=["GET", "POST"])
@login_required
def new_prediction():
    models, ds = load_active_models()
    if request.method == "POST":
        if models is None:
            flash(BLOCK_MESSAGE, "error")
            return redirect(url_for("prediction.new_prediction"))
        errors = _validate_form(request.form)
        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("prediction.html", user=current_user(),
                                   dataset=ds, sample=SAMPLE_APPLICANT,
                                   form_data=request.form)
        applicant = {
            "no_of_dependents": int(request.form["no_of_dependents"]),
            "education": request.form["education"],
            "self_employed": request.form["self_employed"],
            "income_annum": float(request.form["income_annum"]),
            "loan_amount": float(request.form["loan_amount"]),
            "loan_term": int(request.form["loan_term"]),
            "cibil_score": int(request.form["cibil_score"]),
            "residential_assets_value": float(request.form["residential_assets_value"]),
            "commercial_assets_value": float(request.form["commercial_assets_value"]),
            "luxury_assets_value": float(request.form["luxury_assets_value"]),
            "bank_asset_value": float(request.form["bank_asset_value"]),
        }
        result = predict_all(models, applicant)
        votes = result["votes"]
        record = Prediction(
            user_id=current_user().id,
            dataset_id=ds.id,
            no_of_dependents=applicant["no_of_dependents"],
            education=applicant["education"],
            self_employed=applicant["self_employed"],
            income_annum=applicant["income_annum"],
            loan_amount=applicant["loan_amount"],
            loan_term=applicant["loan_term"],
            cibil_score=applicant["cibil_score"],
            residential_assets_value=applicant["residential_assets_value"],
            commercial_assets_value=applicant["commercial_assets_value"],
            luxury_assets_value=applicant["luxury_assets_value"],
            bank_asset_value=applicant["bank_asset_value"],
            dt_pred=votes["Decision Tree"],
            rf_pred=votes["Random Forest"],
            nb_pred=votes["Naive Bayes"],
            knn_pred=votes["KNN"],
            lr_pred=votes["Logistic Regression"],
            approval_votes=result["approval_votes"],
            rejection_votes=result["rejection_votes"],
            final_decision=result["final_decision"],
        )
        db.session.add(record)
        db.session.commit()
        return redirect(url_for("prediction.result", prediction_id=record.id))
    return render_template("prediction.html", user=current_user(),
                           dataset=ds, sample=SAMPLE_APPLICANT, form_data=None,
                           blocked=(models is None))


@prediction_bp.route("/prediction/result/<int:prediction_id>")
@login_required
def result(prediction_id):
    record = Prediction.query.get_or_404(prediction_id)
    return render_template("result.html", user=current_user(), prediction=record)


@prediction_bp.route("/prediction/history")
@login_required
def history():
    """Prediction History - search, filter by decision, sort by date."""
    query = Prediction.query
    search = request.args.get("q", "").strip()
    decision = request.args.get("decision", "").strip()
    sort = request.args.get("sort", "newest")
    if decision in ("APPROVED", "REJECTED", "FURTHER REVIEW"):
        query = query.filter_by(final_decision=decision)
    if search:
        try:
            query = query.filter(
                (Prediction.cibil_score == int(search)) |
                (Prediction.id == int(search))
            )
        except ValueError:
            pass
    query = query.order_by(Prediction.created_at.desc() if sort != "oldest"
                           else Prediction.created_at.asc())
    records = query.all()
    return render_template("history.html", user=current_user(), records=records,
                           search=search, decision=decision, sort=sort)


@prediction_bp.route("/prediction/history/<int:prediction_id>/delete", methods=["POST"])
@login_required
def delete_prediction(prediction_id):
    record = Prediction.query.get_or_404(prediction_id)
    db.session.delete(record)
    db.session.commit()
    flash(f"Prediction #{prediction_id} deleted.", "success")
    return redirect(url_for("prediction.history"))
