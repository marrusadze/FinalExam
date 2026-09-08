#API tests: JSON responses, HTTP methods, and API-key authentication.

from app.models import Event

HEADERS = {"X-API-Key": "test-api-key"}  # matches TestingConfig.API_KEY

NEW_EVENT = {
    "title": "API Created Event",
    "short_description": "made over http",
    "full_description": "A full description for the API-created event.",
    "location": "Tbilisi",
    "event_date": "2030-05-01T18:00",
    "ticket_price": 12.5,
    "organizer": "API Client",
    "category": "Tech",
}


def test_list_events_returns_json(client, event_by_a):
    response = client.get("/api/events")
    assert response.status_code == 200
    assert response.is_json
    body = response.get_json()
    assert body["count"] == 1
    assert body["events"][0]["title"] == "Alice's Concert"


def test_get_single_event(client, event_by_a):
    response = client.get(f"/api/events/{event_by_a.id}")
    assert response.status_code == 200
    assert response.get_json()["location"] == "Tbilisi"


def test_get_missing_event_returns_json_404(client):
    response = client.get("/api/events/99999")
    assert response.status_code == 404
    assert response.get_json()["error"]


def test_create_requires_api_key(client, user_a):
    response = client.post("/api/events", json=NEW_EVENT)
    assert response.status_code == 401


def test_create_with_api_key_succeeds(client, db, user_a):
    response = client.post("/api/events", json=NEW_EVENT, headers=HEADERS)
    assert response.status_code == 201
    new_id = response.get_json()["id"]
    assert db.session.get(Event, new_id) is not None


def test_patch_updates_only_sent_fields(client, db, user_a, event_by_a):
    response = client.patch(
        f"/api/events/{event_by_a.id}", json={"title": "Patched"}, headers=HEADERS
    )
    assert response.status_code == 200
    refreshed = db.session.get(Event, event_by_a.id)
    assert refreshed.title == "Patched"
    assert refreshed.location == "Tbilisi"  # unchanged


def test_delete_with_api_key(client, db, user_a, event_by_a):
    event_id = event_by_a.id
    response = client.delete(f"/api/events/{event_id}", headers=HEADERS)
    assert response.status_code == 200
    assert db.session.get(Event, event_id) is None


def test_create_rejects_bad_category(client, user_a):
    bad = dict(NEW_EVENT, category="Nonsense")
    response = client.post("/api/events", json=bad, headers=HEADERS)
    assert response.status_code == 400
