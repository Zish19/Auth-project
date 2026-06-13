from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.routes.auth import USERS

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_users():
    USERS.clear()
    yield
    USERS.clear()

def test_register_success():
    response = client.post(
        "/auth/register",
        json={"username": "testuser", "public_key": "testkey"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "User registered"}
    assert USERS.get("testuser") == "testkey"

def test_register_duplicate_username():
    # Register first time
    client.post(
        "/auth/register",
        json={"username": "testuser", "public_key": "testkey"}
    )

    # Try to register again
    response = client.post(
        "/auth/register",
        json={"username": "testuser", "public_key": "anotherkey"}
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Username already exists"}
    # Verify the key wasn't overwritten
    assert USERS.get("testuser") == "testkey"
