from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.config import settings

client = TestClient(app)

def test_logout_success():
    with patch("app.routes.auth.destroy_session") as mock_destroy:
        # Set cookie for the request
        client.cookies.set(settings.COOKIE_NAME, "mock_session_id")

        response = client.post("/auth/logout")

        assert response.status_code == 200
        assert response.json() == {"message": "Logged out"}

        # Verify destroy_session was called with the correct sid
        mock_destroy.assert_called_once_with("mock_session_id")

        # In fastapi, deleting a cookie sets it in the response with a specific format (usually max_age=0, expires, etc.)
        # Let's check the Set-Cookie header
        set_cookie = response.headers.get("set-cookie")
        assert set_cookie is not None
        assert f'{settings.COOKIE_NAME}=""' in set_cookie
        assert "Max-Age=0" in set_cookie or "expires=" in set_cookie.lower()

def test_logout_no_cookie():
    with patch("app.routes.auth.destroy_session") as mock_destroy:
        # Clear cookies before test to avoid state bleeding from previous test
        client.cookies.clear()

        response = client.post("/auth/logout")

        assert response.status_code == 200
        assert response.json() == {"message": "Logged out"}

        # Verify destroy_session was called with None because there was no cookie
        mock_destroy.assert_called_once_with(None)
