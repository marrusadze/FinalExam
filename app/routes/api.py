"""
JSON REST API for events.

Covers the syllabus point "Flask RESTful API": resource-oriented endpoints,
standard HTTP methods (GET / POST / PUT / PATCH / DELETE), JSON responses, and
API-key authentication for the write operations.

Design notes:
- Read endpoints (GET) are public.
- Write endpoints require the header ``X-API-Key`` to match ``API_KEY`` from the
  config. This is the simplest scheme from the lecture ("API Key - a token in a
  header"); it identifies a trusted client, not an end user, so events created
  through the API are attributed to the first registered account.
- The API is stateless: no session, no cookies -> CSRF does not apply, so the
  blueprint is exempted from CSRFProtect in ``app/__init__.py``.
"""

import logging
from datetime import datetime
from functools import wraps

from flask import Blueprint, current_app, jsonify, request

from app.extensions import db
from app.models import CATEGORIES, Event, User

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api")


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def event_to_dict(event):
    """Serialize an Event (and a slim view of its author) to a JSON-ready dict."""
    return {
        "id": event.id,
        "title": event.title,
        "short_description": event.short_description,
        "full_description": event.full_description,
        "location": event.location,
        "event_date": event.event_date.isoformat(),
        "ticket_price": event.ticket_price,
        "organizer": event.organizer,
        "category": event.category,
        "posted_at": event.posted_at.isoformat() if event.posted_at else None,
        "author": {"id": event.author.id, "name": event.author.name},
    }


def require_api_key(view):
    """Decorator: reject the request with 401 unless a valid X-API-Key is sent."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        expected = current_app.config.get("API_KEY", "")
        provided = request.headers.get("X-API-Key", "")
        if not expected or provided != expected:
            logger.warning(
                "API auth failed: %s %s", request.method, request.path
            )
            return jsonify(error="Invalid or missing API key"), 401
        return view(*args, **kwargs)

    return wrapped


def _parse_event_payload(data, partial=False):
    """Validate an incoming JSON body.

    Returns ``(fields, None)`` on success or ``(None, (json_response, status))``
    on failure. With ``partial=True`` (PATCH) only the provided keys are checked.
    """
    fields = {}
    required = [
        "title",
        "short_description",
        "full_description",
        "location",
        "event_date",
        "organizer",
    ]

    if not partial:
        missing = [f for f in required if not data.get(f)]
        if missing:
            return None, (jsonify(error="Missing required fields", fields=missing), 400)

    for key in ("title", "short_description", "full_description", "location", "organizer"):
        if key in data:
            fields[key] = str(data[key]).strip()

    if "event_date" in data:
        try:
            fields["event_date"] = datetime.fromisoformat(data["event_date"])
        except (TypeError, ValueError):
            return None, (
                jsonify(error="event_date must be ISO format, e.g. 2026-09-13T19:00"),
                400,
            )

    if "ticket_price" in data:
        try:
            price = float(data["ticket_price"])
        except (TypeError, ValueError):
            return None, (jsonify(error="ticket_price must be a number"), 400)
        if price < 0:
            return None, (jsonify(error="ticket_price cannot be negative"), 400)
        fields["ticket_price"] = price

    if "category" in data:
        if data["category"] not in CATEGORIES:
            return None, (
                jsonify(error="Unknown category", allowed=CATEGORIES),
                400,
            )
        fields["category"] = data["category"]

    return fields, None


# --------------------------------------------------------------------------- #
# read endpoints (public)
# --------------------------------------------------------------------------- #
@api_bp.get("/events")
def list_events():
    """GET /api/events?category=Music&q=tbilisi - list events as JSON."""
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

    events = query.order_by(Event.event_date.asc()).all()
    return jsonify(count=len(events), events=[event_to_dict(e) for e in events])


@api_bp.get("/events/<int:event_id>")
def get_event(event_id):
    """GET /api/events/<id> - a single event as JSON."""
    event = db.session.get(Event, event_id)
    if event is None:
        return jsonify(error="Event not found"), 404
    return jsonify(event_to_dict(event))


# --------------------------------------------------------------------------- #
# write endpoints (X-API-Key required)
# --------------------------------------------------------------------------- #
@api_bp.post("/events")
@require_api_key
def create_event():
    """POST /api/events - create an event from a JSON body."""
    owner = User.query.order_by(User.id).first()
    if owner is None:
        return jsonify(error="No user account exists to own the event"), 409

    data = request.get_json(silent=True) or {}
    fields, error = _parse_event_payload(data, partial=False)
    if error:
        return error

    event = Event(user_id=owner.id, **fields)
    db.session.add(event)
    db.session.commit()
    logger.info("API: event created id=%s (%r)", event.id, event.title)
    return jsonify(event_to_dict(event)), 201


@api_bp.put("/events/<int:event_id>")
@require_api_key
def replace_event(event_id):
    """PUT /api/events/<id> - full update: every field must be supplied."""
    event = db.session.get(Event, event_id)
    if event is None:
        return jsonify(error="Event not found"), 404

    data = request.get_json(silent=True) or {}
    fields, error = _parse_event_payload(data, partial=False)
    if error:
        return error

    for key, value in fields.items():
        setattr(event, key, value)
    db.session.commit()
    logger.info("API: event replaced id=%s", event.id)
    return jsonify(event_to_dict(event))


@api_bp.patch("/events/<int:event_id>")
@require_api_key
def update_event(event_id):
    """PATCH /api/events/<id> - partial update: only the sent fields change."""
    event = db.session.get(Event, event_id)
    if event is None:
        return jsonify(error="Event not found"), 404

    data = request.get_json(silent=True) or {}
    fields, error = _parse_event_payload(data, partial=True)
    if error:
        return error
    if not fields:
        return jsonify(error="No updatable fields supplied"), 400

    for key, value in fields.items():
        setattr(event, key, value)
    db.session.commit()
    logger.info("API: event patched id=%s (%s)", event.id, ", ".join(fields))
    return jsonify(event_to_dict(event))


@api_bp.delete("/events/<int:event_id>")
@require_api_key
def delete_event(event_id):
    """DELETE /api/events/<id> - remove an event."""
    event = db.session.get(Event, event_id)
    if event is None:
        return jsonify(error="Event not found"), 404

    db.session.delete(event)
    db.session.commit()
    logger.info("API: event deleted id=%s", event_id)
    return jsonify(deleted=event_id)


# --------------------------------------------------------------------------- #
# blueprint-local error handlers -> keep the API JSON-only
# --------------------------------------------------------------------------- #
@api_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify(error="Method not allowed"), 405


@api_bp.errorhandler(415)
def unsupported_media_type(error):
    return jsonify(error="Request body must be JSON"), 415
