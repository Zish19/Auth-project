import json
from unittest import mock
from app.services.challenge_service import create_challenge, get_challenge
from app.db import r
from app.config import settings

def test_create_challenge():
    username = "testuser"

    # Store initial state or clear redis state for tests if needed
    r.store.clear()
    r._ttls.clear()

    # Call the function
    challenge_id, challenge = create_challenge(username)

    # Assert return types and lengths
    assert isinstance(challenge_id, str)
    assert len(challenge_id) > 0
    assert isinstance(challenge, str)
    assert len(challenge) > 0

    # Assert data was stored in redis
    key = f"challenge:{challenge_id}"
    stored_data = r.get(key)
    assert stored_data is not None

    # Assert payload correctness
    payload = json.loads(stored_data)
    assert payload["username"] == username
    assert payload["challenge"] == challenge
    assert payload["used"] is False

    # Assert TTL was set correctly
    ttl = r.ttl(key)
    assert ttl == settings.CHALLENGE_TTL_SECONDS


def test_get_challenge_success():
    r.store.clear()
    r._ttls.clear()

    challenge_id, challenge = create_challenge("testuser")

    res = get_challenge(challenge_id)
    assert res is not None
    assert res["username"] == "testuser"
    assert res["challenge"] == challenge
    assert res["used"] is False


def test_get_challenge_missing_data():
    r.store.clear()
    res = get_challenge("nonexistent")
    assert res is None


def test_get_challenge_exception_in_redis():
    with mock.patch("app.services.challenge_service.r.get", side_effect=Exception("Redis error")):
        res = get_challenge("some_id")
        assert res is None


def test_get_challenge_invalid_json():
    r.store.clear()
    r.setex("challenge:invalid_json", 60, "invalid json {")

    res = get_challenge("invalid_json")
    assert res is None


def test_get_challenge_invalid_shape():
    r.store.clear()
    r.setex("challenge:invalid_shape", 60, json.dumps(["not", "a", "dict"]))

    res = get_challenge("invalid_shape")
    assert res is None


def test_get_challenge_missing_fields():
    r.store.clear()
    # Missing 'used'
    incomplete_payload = {"username": "testuser", "challenge": "abc"}
    r.setex("challenge:missing_fields", 60, json.dumps(incomplete_payload))

    res = get_challenge("missing_fields")
    assert res is None
