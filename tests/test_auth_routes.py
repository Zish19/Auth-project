import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routes.auth import USERS

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_users():
    """Clear the USERS dictionary before each test to ensure a clean state."""
    USERS.clear()
    yield

def test_register_success():
    """Test successful user registration."""
    response = client.post(
        "/auth/register",
        json={"username": "testuser", "public_key": "testpublickey"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "User registered"}
    assert "testuser" in USERS
    assert USERS["testuser"] == "testpublickey"

def test_register_existing_user():
    """Test registration when the username already exists."""
    # Register the user first
    USERS["existinguser"] = "existingpublickey"

    # Try to register the same user again
    response = client.post(
        "/auth/register",
        json={"username": "existinguser", "public_key": "newpublickey"}
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Username already exists"}
    # Verify the public key was not overwritten
    assert USERS["existinguser"] == "existingpublickey"

def test_register_invalid_request():
    """Test registration with invalid payload."""
    # Missing public_key
    response = client.post(
        "/auth/register",
        json={"username": "testuser"}
    )
    assert response.status_code == 422

    # Missing username
    response = client.post(
        "/auth/register",
        json={"public_key": "testpublickey"}
    )
    assert response.status_code == 422
