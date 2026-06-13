from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.main import app
from backend.config import settings

@patch("app.routes.auth.get_session")
def test_me_no_cookie(mock_get_session):
    client = TestClient(app)
    mock_get_session.return_value = None
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    mock_get_session.assert_called_once_with(None)

@patch("app.routes.auth.get_session")
def test_me_invalid_cookie(mock_get_session):
    client = TestClient(app)
    mock_get_session.return_value = None
    client.cookies.set(settings.COOKIE_NAME, "invalid_session_id")

    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    mock_get_session.assert_called_once_with("invalid_session_id")

@patch("app.routes.auth.get_session")
def test_me_valid_cookie(mock_get_session):
    client = TestClient(app)
    mock_get_session.return_value = {"username": "testuser"}
    client.cookies.set(settings.COOKIE_NAME, "valid_session_id")

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json() == {"username": "testuser"}
    mock_get_session.assert_called_once_with("valid_session_id")
