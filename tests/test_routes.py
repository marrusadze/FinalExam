"""Route test: public pages should load without requiring authentication."""


def test_index_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    # "მომავალი ივენთები" heading is rendered on the events index
    assert "ივენთები".encode() in response.data


def test_about_page_loads(client):
    response = client.get("/about")
    assert response.status_code == 200


def test_event_detail_page(client, event_by_a):
    response = client.get(f"/events/{event_by_a.id}")
    assert response.status_code == 200
    assert b"Concert" in response.data
    assert b"Tbilisi" in response.data


def test_unknown_route_returns_404(client):
    response = client.get("/this-route-does-not-exist")
    assert response.status_code == 404


def test_add_event_requires_login(client):
    # anonymous users should be redirected to the login page, not allowed through
    response = client.get("/events/add", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
