"""LoanWise AI - dashboard route.

Every number on the dashboard comes from the real uploaded dataset
and the real prediction records. Before any dataset is uploaded and
trained, the page shows the empty state - no fake statistics.
"""
import json

from flask import Blueprint, render_template

from database.db import Prediction
from routes.common import active_dataset, current_user, login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    ds = active_dataset()
    total_predictions = Prediction.query.count()
    recent = Prediction.query.order_by(Prediction.created_at.desc()).limit(8).all()
    stats = None
    metrics = None
    best_model = None
    if ds is not None:
        metrics = json.loads(ds.metrics_json) if ds.metrics_json else None
        if metrics:
            best_model = max(metrics, key=lambda n: (metrics[n]["accuracy"], metrics[n]["f1"]))
        stats = {
            "total": ds.total_rows,
            "approved": ds.approved,
            "rejected": ds.rejected,
            "predictions": total_predictions,
            "best_accuracy": (metrics[best_model]["accuracy"] * 100) if metrics else None,
            "best_model": best_model,
        }
    return render_template(
        "dashboard.html",
        user=current_user(),
        dataset=ds,
        stats=stats,
        metrics=metrics,
        best_model=best_model,
        recent=recent,
        total_predictions=total_predictions,
    )
