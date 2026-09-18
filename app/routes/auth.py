from flask_login import login_user, logout_user, login_required
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

import re

from app import db
from app.models.user import User


auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # Check username
        if not username:
            flash("Username is required.")
            return redirect(url_for("auth.register"))

        # Check email
        email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        if not re.match(email_pattern, email):
            flash("Please enter a valid email address.")
            return redirect(url_for("auth.register"))

        # Check password
        if not password:
            flash("Password is required.")
            return redirect(url_for("auth.register"))

        # Check password confirmation
        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("auth.register"))

        # Check existing username or email
        existing_user = User.query.filter(
            (User.username == username) |
            (User.email == email)
        ).first()

        if existing_user:
            flash("Username or email already exists.")
            return redirect(url_for("auth.register"))

        # Create new user
        user = User(
            username=username,
            email=email
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash(
            "Registration successful! "
            "Please login."
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "auth/register.html"
    )


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")

    return render_template("auth/login.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("auth.login"))