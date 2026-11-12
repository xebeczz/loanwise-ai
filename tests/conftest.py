"""Pytest fixtures: a fresh LoanWise app with a temporary database
and temporary upload/model folders, so tests never touch real data.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app  # noqa: E402
from config import Config  # noqa: E402
from database.db import db  # noqa: E402


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret"


@pytest.fixture()
def app(tmp_path):
    cfg = TestConfig
    cfg.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(tmp_path / "test.db")
    cfg.UPLOAD_FOLDER = str(tmp_path / "uploads")
    cfg.MODEL_FOLDER = str(tmp_path / "models")
    cfg.CHART_FOLDER = str(tmp_path / "charts")
    cfg.REPORT_FOLDER = str(tmp_path / "reports")
    application = create_app(cfg)
    with application.app_context():
        db.create_all()
    yield application
    with application.app_context():
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def logged_in(client):
    """Register + log in a test user, return the client."""
    client.post("/register", data={
        "name": "Test User", "email": "test@example.com",
        "password": "secret123", "confirm_password": "secret123",
    }, follow_redirects=True)
    return client


@pytest.fixture()
def sample_csv(tmp_path):
    """A small VALID loan CSV (same columns as the real dataset)."""
    import pandas as pd
    rows = []
    for i in range(60):
        approved = i % 3 != 0
        rows.append({
            "loan_id": i + 1, "no_of_dependents": i % 3,
            "education": "Graduate" if i % 2 == 0 else "Not Graduate",
            "self_employed": "Yes" if i % 4 == 0 else "No",
            "income_annum": 900000 + i * 100000,
            "loan_amount": 500000 + i * 100000,
            "loan_term": 5 + (i % 10),
            "cibil_score": 750 if approved else 450,
            "residential_assets_value": 1000000 + i * 10000,
            "commercial_assets_value": 500000 + i * 5000,
            "luxury_assets_value": 800000 + i * 8000,
            "bank_asset_value": 600000 + i * 6000,
            "loan_status": "Approved" if approved else "Rejected",
        })
    path = tmp_path / "sample.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path
