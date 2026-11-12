"""LoanWise AI - configuration.

Keep it simple for a college viva: one file, plain values,
no environment variables required to run on Windows.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # SECRET_KEY comes from the environment on Render (render.yaml
    # generates one); the dev value below is local-only fallback.
    SECRET_KEY = os.environ.get("SECRET_KEY", "loanwise-ai-dev-secret-key")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "loanwise.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 20 MB maximum CSV upload (see spec section 5A)
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "datasets")
    MODEL_FOLDER = os.path.join(BASE_DIR, "models", "saved_models")
    CHART_FOLDER = os.path.join(BASE_DIR, "static", "charts")
    REPORT_FOLDER = os.path.join(BASE_DIR, "reports")
