from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.config import settings

client = TestClient(app)

@patch("app.routes.auth.get_session")
def test_me_success(mock_get_session):
    mock_get_session.return_value = {"username": "testuser"}

    # Set the cookie explicitly for the TestClient
    client.cookies.set(settings.COOKIE_NAME, "valid_sid")

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json() == {"username": "testuser"}
    mock_get_session.assert_called_once_with("valid_sid")

@patch("app.routes.auth.get_session")
def test_me_invalid_session(mock_get_session):
    mock_get_session.return_value = None

    client.cookies.set(settings.COOKIE_NAME, "invalid_sid")

    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    mock_get_session.assert_called_once_with("invalid_sid")

@patch("app.routes.auth.get_session")
def test_me_no_cookie(mock_get_session):
    mock_get_session.return_value = None

    # Ensure no cookies are set
    client.cookies.clear()

    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    mock_get_session.assert_called_once_with(None)
