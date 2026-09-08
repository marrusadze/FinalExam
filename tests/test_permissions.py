#Permission test: a user must not be able to edit or delete someone else's event.

from app.models import Event
from tests.conftest import login


def test_cannot_edit_someone_elses_event(client, db, user_a, user_b, event_by_a):
    login(client, "bob@example.com", "password456")

    response = client.get(f"/events/{event_by_a.id}/edit")
    assert response.status_code == 403

    response = client.post(
        f"/events/{event_by_a.id}/edit",
        data={
            "title": "Hacked title",
            "short_description": "hacked",
            "full_description": "hacked",
            "location": "Nowhere",
            "event_date": "2030-01-01T10:00",
            "ticket_price": "0",
            "organizer": "Hacker",
            "category": "Other",
        },
    )
    assert response.status_code == 403

    unchanged = db.session.get(Event, event_by_a.id)
    assert unchanged.title == "Alice's Concert"


def test_cannot_delete_someone_elses_event(client, db, user_a, user_b, event_by_a):
    login(client, "bob@example.com", "password456")

    response = client.post(f"/events/{event_by_a.id}/delete")
    assert response.status_code == 403

    still_there = db.session.get(Event, event_by_a.id)
    assert still_there is not None


def test_owner_can_edit_own_event(client, db, user_a, event_by_a):
    login(client, "alice@example.com", "password123")

    response = client.post(
        f"/events/{event_by_a.id}/edit",
        data={
            "title": "Updated Concert Title",
            "short_description": "Updated",
            "full_description": "Updated full description.",
            "location": "Tbilisi",
            "event_date": "2030-01-01T10:00",
            "ticket_price": "30",
            "organizer": "Alice Productions",
            "category": "Music",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    updated = db.session.get(Event, event_by_a.id)
    assert updated.title == "Updated Concert Title"
