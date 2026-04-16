import json
import logging
import secrets
from app.config import settings
from app.db import r

logger = logging.getLogger(__name__)


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
    try:
        data = r.get(key)
    except Exception:
        logger.exception("auth.challenge.fetch_failed", extra={"challenge_id": challenge_id})
        return None

    if not data:
        return None

    try:
        challenge = json.loads(data)
    except (TypeError, json.JSONDecodeError):
        logger.warning(
            "auth.challenge.invalid_payload",
            extra={"challenge_id": challenge_id},
        )
        return None

    if not isinstance(challenge, dict):
        logger.warning(
            "auth.challenge.invalid_shape",
            extra={"challenge_id": challenge_id},
        )
        return None

    required_fields = {"username", "challenge", "used"}
    if not required_fields.issubset(challenge.keys()):
        logger.warning(
            "auth.challenge.missing_fields",
            extra={"challenge_id": challenge_id},
        )
        return None

    return challenge


def mark_challenge_used(challenge_id: str):
    key = f"challenge:{challenge_id}"
    try:
        data = r.get(key)
    except Exception:
        logger.exception("auth.challenge.read_for_mark_failed", extra={"challenge_id": challenge_id})
        return False

    if not data:
        return False

    try:
        obj = json.loads(data)
    except (TypeError, json.JSONDecodeError):
        logger.warning(
            "auth.challenge.mark_invalid_payload",
            extra={"challenge_id": challenge_id},
        )
        return False

    obj["used"] = True

    try:
        ttl = r.ttl(key)
        r.setex(key, max(ttl, 1), json.dumps(obj))
    except Exception:
        logger.exception("auth.challenge.mark_used_failed", extra={"challenge_id": challenge_id})
        return False

    return True