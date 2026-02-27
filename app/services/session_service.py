import json
import secrets
from app.config import settings
from app.db import r


def create_session(username: str):
    sid = secrets.token_urlsafe(32)
    key = f"session:{sid}"
    payload = {"username": username}
    r.setex(key, settings.SESSION_TTL_SECONDS, json.dumps(payload))
    return sid


def get_session(sid: str):
    if not sid:
        return None

    data = r.get(f"session:{sid}")
    if not data:
        return None

    return json.loads(data)


def destroy_session(sid: str):
    if sid:
        r.delete(f"session:{sid}")