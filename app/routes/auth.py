import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.forms import LoginForm, RegisterForm
from app.models import User

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("events.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if existing:
            flash("ამ ელფოსტით ანგარიში უკვე არსებობს.", "danger")
            logger.warning(
                "Failed registration attempt: email already in use (%s)", form.email.data
            )
            return render_template("auth/register.html", form=form)

        user = User(name=form.name.data.strip(), email=form.email.data.lower().strip())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        logger.info("New user registered: %s (id=%s)", user.email, user.id)
        flash("ანგარიში წარმატებით შეიქმნა. გაიარეთ ავტორიზაცია.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("events.index"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            logger.info("Successful login: %s (id=%s)", user.email, user.id)
            flash(f"კეთილი იყოს თქვენი დაბრუნება, {user.name}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("events.index"))

        logger.warning("Failed login attempt for email: %s", email)
        flash("ელფოსტა ან პაროლი არასწორია.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logger.info("User logged out: %s (id=%s)", current_user.email, current_user.id)
    logout_user()
    flash("თქვენ გამოხვედით სისტემიდან.", "info")
    return redirect(url_for("events.index"))
