"""Tests for the Render-only auto-seed (seed.py).

The seed must NEVER run on a local run, must restore a trained demo
on Render when the database is empty, and must never re-seed or
hijack an existing dataset.
"""
import os

from app import create_app
from database.db import Dataset, User, db
from seed import DEMO_EMAIL, DEMO_PASSWORD, seed_demo_if_needed
from tests.conftest import TestConfig


def _fresh_app(tmp_path):
    cfg = TestConfig
    cfg.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(tmp_path / "seed.db")
    cfg.UPLOAD_FOLDER = str(tmp_path / "uploads")
    cfg.MODEL_FOLDER = str(tmp_path / "models")
    cfg.CHART_FOLDER = str(tmp_path / "charts")
    cfg.REPORT_FOLDER = str(tmp_path / "reports")
    application = create_app(cfg)
    with application.app_context():
        db.create_all()
    return application


def test_seed_disabled_locally(tmp_path, monkeypatch):
    """No RENDER / FLASK_ENV=production -> seed does nothing."""
    monkeypatch.delenv("RENDER", raising=False)
    monkeypatch.delenv("FLASK_ENV", raising=False)
    monkeypatch.delenv("LOANWISE_AUTO_SEED", raising=False)
    application = _fresh_app(tmp_path)
    assert seed_demo_if_needed(application) is False
    with application.app_context():
        assert Dataset.query.count() == 0
        assert User.query.filter_by(email=DEMO_EMAIL).first() is None


def test_seed_disabled_by_flag_even_on_render(tmp_path, monkeypatch):
    monkeypatch.setenv("RENDER", "1")
    monkeypatch.setenv("LOANWISE_AUTO_SEED", "0")
    application = _fresh_app(tmp_path)
    assert seed_demo_if_needed(application) is False
    with application.app_context():
        assert Dataset.query.count() == 0


def test_seed_restores_demo_on_render(tmp_path, monkeypatch):
    """RENDER=1 + empty DB -> trained demo dataset + demo account.

    Note: create_app() itself calls the seed at startup, so by the
    time _fresh_app() returns the demo is already seeded; calling the
    seed again must then return False (idempotent, no re-seed).
    """
    monkeypatch.setenv("RENDER", "1")
    monkeypatch.delenv("LOANWISE_AUTO_SEED", raising=False)
    application = _fresh_app(tmp_path)
    with application.app_context():
        assert Dataset.query.filter_by(is_active=True, status="trained").first() is not None
    with application.app_context():
        ds = Dataset.query.filter_by(is_active=True, status="trained").first()
        assert ds is not None
        assert ds.total_rows == 4269
        assert ds.approved == 2656
        assert ds.rejected == 1613
        assert ds.train_count == 2988
        assert ds.test_count == 1281
        assert "Random Forest" in (ds.metrics_json or "")
        user = User.query.filter_by(email=DEMO_EMAIL).first()
        assert user is not None
    # Second call must NOT re-seed.
    assert seed_demo_if_needed(application) is False
    with application.app_context():
        assert Dataset.query.count() == 1
    # Demo account can actually log in.
    client = application.test_client()
    resp = client.post("/login", data={
        "email": DEMO_EMAIL, "password": DEMO_PASSWORD,
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Dashboard" in resp.data
    assert b"4,269" in resp.data
