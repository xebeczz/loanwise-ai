"""LoanWise AI - authentication routes.

Flask sessions (no Flask-Login, per spec). Passwords are hashed with
Werkzeug's generate_password_hash / check_password_hash - never stored
in plain text. First user registers on the Register page; every page
except login/register/forgot requires a session.
"""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import User, db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_email"] = user.email
            session.permanent = bool(request.form.get("remember"))
            flash("Welcome back to LoanWise AI.", "success")
            return redirect(url_for("dashboard.dashboard"))
        flash("Invalid email or password. Please try again.", "error")
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if not name or not email or not password:
            flash("All fields are required.", "error")
        elif len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        elif User.query.filter_by(email=email).first():
            flash("An account with this email already exists. Please sign in.", "error")
        else:
            user = User(name=name, email=email,
                        password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_email"] = user.email
            flash("Account created. Welcome to LoanWise AI.", "success")
            return redirect(url_for("dashboard.dashboard"))
    return render_template("register.html")


@auth_bp.route("/forgot", methods=["GET", "POST"])
def forgot():
    """Forgot-password page.

    This is a college demo with no email server, so the reset works
    directly: enter your registered email and a new password. In a
    production system this step would send a reset link by email.
    """
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("No account found with that email address.", "error")
        elif len(password) < 6:
            flash("New password must be at least 6 characters long.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        else:
            user.password_hash = generate_password_hash(password)
            db.session.commit()
            flash("Password reset. You can now sign in with your new password.", "success")
            return redirect(url_for("auth.login"))
    return render_template("forgot.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("auth.login"))
