import logging

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms import EventForm
from app.models import CATEGORIES, Event, User
from app.weather import get_weather_for_location

logger = logging.getLogger(__name__)

events_bp = Blueprint("events", __name__)


@events_bp.route("/")
def index():
    query = Event.query

    category = request.args.get("category", "").strip()
    if category and category in CATEGORIES:
        query = query.filter(Event.category == category)

    search = request.args.get("q", "").strip()
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(Event.title.ilike(like), Event.location.ilike(like))
        )

    sort = request.args.get("sort", "posted_desc")
    sort_options = {
        "posted_desc": Event.posted_at.desc(),
        "posted_asc": Event.posted_at.asc(),
        "date_asc": Event.event_date.asc(),
        "date_desc": Event.event_date.desc(),
        "price_asc": Event.ticket_price.asc(),
        "price_desc": Event.ticket_price.desc(),
    }
    query = query.order_by(sort_options.get(sort, Event.posted_at.desc()))

    page = request.args.get("page", 1, type=int)
    from flask import current_app

    per_page = current_app.config.get("EVENTS_PER_PAGE", 9)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        "events/index.html",
        pagination=pagination,
        events=pagination.items,
        categories=CATEGORIES,
        current_category=category,
        current_sort=sort,
        search=search,
    )


@events_bp.route("/users/<int:user_id>")
def author_profile(user_id):
    author = db.session.get(User, user_id) or abort(404)
    author_events = (
        Event.query.filter_by(user_id=author.id).order_by(Event.event_date.asc()).all()
    )
    return render_template("events/author.html", author=author, events=author_events)


@events_bp.route("/events/<int:event_id>")
def detail(event_id):
    event = db.session.get(Event, event_id) or abort(404)
    weather = get_weather_for_location(event.location)
    return render_template("events/detail.html", event=event, weather=weather)


@events_bp.route("/events/add", methods=["GET", "POST"])
@login_required
def add():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data.strip(),
            short_description=form.short_description.data.strip(),
            full_description=form.full_description.data.strip(),
            location=form.location.data.strip(),
            event_date=form.event_date.data,
            ticket_price=form.ticket_price.data,
            organizer=form.organizer.data.strip(),
            category=form.category.data,
            user_id=current_user.id,
        )
        db.session.add(event)
        db.session.commit()
        logger.info(
            "Event added: %r (id=%s) by user %s", event.title, event.id, current_user.email
        )
        flash("ივენთი წარმატებით დაემატა.", "success")
        return redirect(url_for("events.detail", event_id=event.id))

    return render_template("events/form.html", form=form, mode="add")


@events_bp.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
def edit(event_id):
    event = db.session.get(Event, event_id) or abort(404)

    if event.user_id != current_user.id:
        logger.warning(
            "Unauthorized edit attempt on event id=%s by user %s", event_id, current_user.email
        )
        abort(403)

    form = EventForm(obj=event)
    if form.validate_on_submit():
        form.populate_obj(event)
        db.session.commit()
        logger.info(
            "Event edited: %r (id=%s) by user %s", event.title, event.id, current_user.email
        )
        flash("ივენთი წარმატებით განახლდა.", "success")
        return redirect(url_for("events.detail", event_id=event.id))

    return render_template("events/form.html", form=form, mode="edit", event=event)


@events_bp.route("/events/<int:event_id>/delete", methods=["POST"])
@login_required
def delete(event_id):
    event = db.session.get(Event, event_id) or abort(404)

    if event.user_id != current_user.id:
        logger.warning(
            "Unauthorized delete attempt on event id=%s by user %s", event_id, current_user.email
        )
        abort(403)

    title = event.title
    db.session.delete(event)
    db.session.commit()
    logger.info("Event deleted: %r (id=%s) by user %s", title, event_id, current_user.email)
    flash("ივენთი წაიშალა.", "info")
    return redirect(url_for("events.index"))
