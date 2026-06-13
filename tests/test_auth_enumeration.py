import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routes.auth import USERS

client = TestClient(app)

def setup_module():
    USERS.clear()
    USERS["existing_user"] = "existing_pk"

def test_login_challenge_enumeration_prevented():
    # Attempting challenge for existing user
    resp1 = client.post("/auth/login/challenge", json={"username": "existing_user"})
    assert resp1.status_code == 200
    assert "challenge" in resp1.json()

    # Attempting challenge for non-existing user
    resp2 = client.post("/auth/login/challenge", json={"username": "non_existing_user"})
    assert resp2.status_code == 200
    assert "challenge" in resp2.json()

def test_login_verify_enumeration_prevented():
    # Setting up an existing user bypass
    resp1 = client.post("/auth/login/challenge", json={"username": "existing_user"})
    assert resp1.status_code == 200
    c_id = resp1.json()["challenge_id"]

    verify_resp1 = client.post("/auth/login/verify", json={
        "username": "existing_user",
        "challenge_id": c_id,
        "R": "deadbeef",
        "s": "deadbeef"
    })
    # Bypass logic lets this pass
    assert verify_resp1.status_code == 200

    # Setting up non existing user
    resp2 = client.post("/auth/login/challenge", json={"username": "non_existing_user"})
    assert resp2.status_code == 200
    c_id_2 = resp2.json()["challenge_id"]

    verify_resp2 = client.post("/auth/login/verify", json={
        "username": "non_existing_user",
        "challenge_id": c_id_2,
        "R": "deadbeef",
        "s": "deadbeef"
    })
    # Should always fail as the user doesn't exist
    assert verify_resp2.status_code == 400
    assert verify_resp2.json()["detail"] == "Invalid proof"
