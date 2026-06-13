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
    payload = {"username": "testuser", "challenge": "abc", "used": False}
    r.setex("challenge:123", 100, json.dumps(payload))
    result = get_challenge("123")
    assert result == payload

def test_get_challenge_not_found():
    r.store.clear()
    assert get_challenge("notfound") is None

@mock.patch("app.services.challenge_service.r.get")
def test_get_challenge_redis_exception(mock_get):
    mock_get.side_effect = Exception("Redis error")
    assert get_challenge("123") is None

def test_get_challenge_invalid_json():
    r.store.clear()
    r.setex("challenge:bad_json", 100, "{bad_json:")
    assert get_challenge("bad_json") is None

def test_get_challenge_invalid_shape():
    r.store.clear()
    r.setex("challenge:list_json", 100, json.dumps(["a", "b"]))
    assert get_challenge("list_json") is None

def test_get_challenge_missing_fields():
    r.store.clear()
    # Missing "used" field
    payload = {"username": "testuser", "challenge": "abc"}
    r.setex("challenge:missing_fields", 100, json.dumps(payload))
    assert get_challenge("missing_fields") is None
