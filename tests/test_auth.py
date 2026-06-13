import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.config import settings

client = TestClient(app)

@patch("app.routes.auth.destroy_session")
def test_logout_with_cookie(mock_destroy_session):
    # Set up the cookie in the TestClient
    client.cookies.set(settings.COOKIE_NAME, "test_sid_123")

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert response.json() == {"message": "Logged out"}

    # Verify destroy_session was called
    mock_destroy_session.assert_called_once_with("test_sid_123")

    # Verify cookie was deleted
    set_cookie = response.headers.get("set-cookie")
    assert set_cookie is not None
    assert settings.COOKIE_NAME in set_cookie
    assert 'Max-Age=0' in set_cookie or 'expires=' in set_cookie.lower()

@patch("app.routes.auth.destroy_session")
def test_logout_without_cookie(mock_destroy_session):
    # Ensure no cookies are set
    client.cookies.clear()

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert response.json() == {"message": "Logged out"}

    # Verify destroy_session was called with None
    mock_destroy_session.assert_called_once_with(None)
