"""Shared helpers for the route blueprints."""
import os
from functools import wraps

from flask import current_app, redirect, session, url_for

from database.db import Dataset, User, db
from ml.training import load_models


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def current_user():
    if "user_id" not in session:
        return None
    return User.query.get(session["user_id"])


def active_dataset():
    """The dataset whose models are currently live, or None.

    Returns None before any manual upload + training - that is the
    normal starting state, not an error. Pages must show an empty
    state in that case, never fake numbers.
    """
    return Dataset.query.filter_by(is_active=True, status="trained").first()


def load_active_models():
    """Load the five saved pipelines for the active dataset, or None."""
    ds = active_dataset()
    if ds is None:
        return None, None
    model_dir = os.path.join(current_app.config["MODEL_FOLDER"], f"dataset_{ds.id}")
    models = load_models(model_dir)
    if models is None:
        return None, None
    return models, ds
