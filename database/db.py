"""LoanWise AI - database models (SQLite + SQLAlchemy).

Tables:
  users       - login accounts (passwords hashed with Werkzeug, never plain text)
  datasets    - one row per manually uploaded CSV (metadata + summary + status)
  predictions - every loan prediction, kept forever (even after dataset replacement)

No dataset is ever bundled or pre-loaded: the datasets table starts empty.
Models are only trained after a user uploads a CSV and clicks
"Process Dataset & Train Models".
"""
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    predictions = db.relationship("Prediction", backref="user", lazy=True)


class Dataset(db.Model):
    __tablename__ = "datasets"
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    # Summary calculated from the ACTUAL uploaded CSV - never hardcoded.
    total_rows = db.Column(db.Integer, nullable=True)
    total_columns = db.Column(db.Integer, nullable=True)
    missing_values = db.Column(db.Integer, nullable=True)
    duplicate_rows = db.Column(db.Integer, nullable=True)
    approved = db.Column(db.Integer, nullable=True)
    rejected = db.Column(db.Integer, nullable=True)
    train_count = db.Column(db.Integer, nullable=True)
    test_count = db.Column(db.Integer, nullable=True)
    # status: uploaded -> training -> trained | failed ; replaced datasets keep status 'replaced'
    status = db.Column(db.String(20), default="uploaded")
    is_active = db.Column(db.Boolean, default=False)
    metrics_json = db.Column(db.Text, nullable=True)  # JSON of the 5 models' metrics
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    trained_at = db.Column(db.DateTime, nullable=True)


class Prediction(db.Model):
    __tablename__ = "predictions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey("datasets.id"), nullable=True)
    # The 11 applicant inputs, stored exactly as entered.
    no_of_dependents = db.Column(db.Integer, nullable=False)
    education = db.Column(db.String(20), nullable=False)
    self_employed = db.Column(db.String(10), nullable=False)
    income_annum = db.Column(db.Float, nullable=False)
    loan_amount = db.Column(db.Float, nullable=False)
    loan_term = db.Column(db.Integer, nullable=False)
    cibil_score = db.Column(db.Integer, nullable=False)
    residential_assets_value = db.Column(db.Float, nullable=False)
    commercial_assets_value = db.Column(db.Float, nullable=False)
    luxury_assets_value = db.Column(db.Float, nullable=False)
    bank_asset_value = db.Column(db.Float, nullable=False)
    # One vote per model: 1 = Approve, 0 = Reject.
    dt_pred = db.Column(db.Integer, nullable=False)
    rf_pred = db.Column(db.Integer, nullable=False)
    nb_pred = db.Column(db.Integer, nullable=False)
    knn_pred = db.Column(db.Integer, nullable=False)
    lr_pred = db.Column(db.Integer, nullable=False)
    approval_votes = db.Column(db.Integer, nullable=False)
    rejection_votes = db.Column(db.Integer, nullable=False)
    final_decision = db.Column(db.String(20), nullable=False)  # APPROVED / REJECTED / FURTHER REVIEW
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def votes(self):
        """Ordered list of (model display name, 1/0) in training order."""
        return [
            ("Decision Tree", self.dt_pred),
            ("Random Forest", self.rf_pred),
            ("Naive Bayes", self.nb_pred),
            ("KNN", self.knn_pred),
            ("Logistic Regression", self.lr_pred),
        ]
