"""LoanWise AI - settings routes (profile + change password)."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import db
from routes.common import current_user, login_required

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    user = current_user()
    if request.method == "POST":
        action = request.form.get("action")
        if action == "profile":
            name = request.form.get("name", "").strip()
            if not name:
                flash("Name cannot be empty.", "error")
            else:
                user.name = name
                db.session.commit()
                flash("Profile updated.", "success")
        elif action == "password":
            current = request.form.get("current_password", "")
            new = request.form.get("new_password", "")
            confirm = request.form.get("confirm_password", "")
            if not check_password_hash(user.password_hash, current):
                flash("Current password is incorrect.", "error")
            elif len(new) < 6:
                flash("New password must be at least 6 characters long.", "error")
            elif new != confirm:
                flash("New passwords do not match.", "error")
            else:
                user.password_hash = generate_password_hash(new)
                db.session.commit()
                flash("Password changed successfully.", "success")
        return redirect(url_for("settings.settings"))
    return render_template("settings.html", user=user)
