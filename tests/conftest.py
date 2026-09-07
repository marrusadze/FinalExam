import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from app.extensions import db as _db
from app.models import Event, User


@pytest.fixture
def app():
    application = create_app("testing")

    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


def _create_user(db, name="Alice", email="alice@example.com", password="password123"):
    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def user_a(db):
    return _create_user(db, "Alice", "alice@example.com", "password123")


@pytest.fixture
def user_b(db):
    return _create_user(db, "Bob", "bob@example.com", "password456")


@pytest.fixture
def event_by_a(db, user_a):
    event = Event(
        title="Alice's Concert",
        short_description="A great show",
        full_description="Full details about Alice's concert.",
        location="Tbilisi",
        event_date=datetime.utcnow() + timedelta(days=7),
        ticket_price=25.0,
        organizer="Alice Productions",
        category="Music",
        user_id=user_a.id,
    )
    db.session.add(event)
    db.session.commit()
    return event


def login(client, email, password):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )
