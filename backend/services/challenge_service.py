import json
import logging
import secrets
from backend.config import settings
from backend.db import r

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


MARK_USED_LUA = """
local key = KEYS[1]
local data = redis.call("GET", key)
if not data then
    return 0
end

local ok, obj = pcall(cjson.decode, data)
if not ok then
    return 0
end

obj.used = true
local new_data = cjson.encode(obj)

local ttl = redis.call("TTL", key)
if ttl < 0 then
    ttl = 60
end
redis.call("SETEX", key, math.max(ttl, 1), new_data)
return 1
"""

def mark_challenge_used(challenge_id: str):
    key = f"challenge:{challenge_id}"
    try:
        result = r.eval(MARK_USED_LUA, 1, key)
        return bool(result)
    except Exception:
        logger.exception("auth.challenge.mark_used_failed", extra={"challenge_id": challenge_id})
        return False