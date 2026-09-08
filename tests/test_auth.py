#Login test: registration + successful/failed login flows.

from tests.conftest import login


def test_register_creates_user(client, db):
    response = client.post(
        "/register",
        data={
            "name": "Carol",
            "email": "carol@example.com",
            "password": "secretpass",
            "confirm_password": "secretpass",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    from app.models import User

    assert User.query.filter_by(email="carol@example.com").first() is not None


def test_login_with_correct_credentials_succeeds(client, user_a):
    response = login(client, "alice@example.com", "password123")
    assert response.status_code == 200
    assert b"Welcome back" in response.data or b"Logout" in response.data or response.request.path == "/"


def test_login_with_wrong_password_fails(client, user_a):
    response = login(client, "alice@example.com", "wrong-password")
    assert response.status_code == 200
    assert "ელფოსტა ან პაროლი არასწორია".encode() in response.data


def test_logout_ends_session(client, user_a):
    login(client, "alice@example.com", "password123")
    response = client.get("/events/add")
    assert response.status_code == 200  # logged in, can access add-event form

    client.get("/logout", follow_redirects=True)
    response = client.get("/events/add", follow_redirects=False)
    assert response.status_code == 302  # logged out, redirected to login
