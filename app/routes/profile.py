import logging
import os
import uuid

from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms import ProfileForm
from app.models import Event

logger = logging.getLogger(__name__)

profile_bp = Blueprint("profile", __name__)


def _allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


@profile_bp.route("/profile", methods=["GET", "POST"])
@login_required
def view():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        new_email = form.email.data.lower().strip()
        if new_email != current_user.email:
            from app.models import User

            if User.query.filter(User.email == new_email, User.id != current_user.id).first():
                flash("ეს ელფოსტა უკვე გამოიყენება სხვა ანგარიშის მიერ.", "danger")
                return render_template("profile/view.html", form=form)

        current_user.name = form.name.data.strip()
        current_user.email = new_email

        file = form.profile_pic.data
        if file and getattr(file, "filename", ""):
            if _allowed_file(file.filename):
                ext = file.filename.rsplit(".", 1)[-1].lower()
                filename = f"user_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
                filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                current_user.profile_pic = filename
            else:
                flash("სურათის ფორმატი მხარდაუჭერელია.", "danger")
                return render_template("profile/view.html", form=form)

        db.session.commit()
        logger.info("Profile updated for user %s (id=%s)", current_user.email, current_user.id)
        flash("პროფილი განახლდა.", "success")
        return redirect(url_for("profile.view"))

    my_events = (
        Event.query.filter_by(user_id=current_user.id)
        .order_by(Event.posted_at.desc())
        .all()
    )
    return render_template("profile/view.html", form=form, my_events=my_events)
