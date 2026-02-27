import json
import secrets
from app.config import settings
from app.db import r


def create_challenge(username: str):
    challenge_id = secrets.token_urlsafe(24)
    challenge = secrets.token_hex(32)

    payload = {
        "username": username,
        "challenge": challenge,
        "used": False
    }

    key = f"challenge:{challenge_id}"
    r.setex(key, settings.CHALLENGE_TTL_SECONDS, json.dumps(payload))

    return challenge_id, challenge


def get_challenge(challenge_id: str):
    key = f"challenge:{challenge_id}"
    data = r.get(key)

    if not data:
        return None

    return json.loads(data)


def mark_challenge_used(challenge_id: str):
    key = f"challenge:{challenge_id}"
    data = r.get(key)

    if not data:
        return False

    obj = json.loads(data)
    obj["used"] = True

    ttl = r.ttl(key)
    r.setex(key, max(ttl, 1), json.dumps(obj))

    return True