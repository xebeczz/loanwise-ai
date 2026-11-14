"""LoanWise AI - Machine Learning-Based Loan Approval Decision Support System.

Run:  python app.py        then open http://localhost:5000
First: register an account, then go to Dataset Management and upload
your loan CSV manually. Models are trained ONLY when you click
"Process Dataset & Train Models" - nothing is bundled or auto-trained
on a LOCAL run.

One exception, on Render only: see seed.py. Render's free disk wipes
the database on every restart, so on Render (and only there) the app
auto-restores the bundled demo dataset + demo account at startup when
the database is empty. Local runs are unaffected.
"""
import os

from flask import Flask

from config import Config
from database.db import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    for folder in (app.config["UPLOAD_FOLDER"], app.config["MODEL_FOLDER"],
                   app.config["CHART_FOLDER"], app.config["REPORT_FOLDER"]):
        os.makedirs(folder, exist_ok=True)

    db.init_app(app)
    with app.app_context():
        db.create_all()
    # Render-only auto-seed (see seed.py): after a free-tier wipe the
    # database is empty, so restore the demo dataset + demo account.
    # Local runs skip this - they stay manual-upload-only.
    from seed import seed_demo_if_needed

    seed_demo_if_needed(app)

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.dataset import dataset_bp
    from routes.prediction import prediction_bp
    from routes.reports import reports_bp
    from routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(dataset_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    return app


app = create_app()

if __name__ == "__main__":
    # Local run: http://localhost:5000, debug on for clear error pages.
    # On Render (RENDER env var set, or FLASK_ENV=production), bind
    # 0.0.0.0 on $PORT with debug off. Gunicorn does not use this
    # block at all - it imports `app` above and serves it directly.
    on_render = "RENDER" in os.environ or os.environ.get("FLASK_ENV") == "production"
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0" if on_render else "127.0.0.1",
            port=port, debug=not on_render)
