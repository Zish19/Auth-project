import json
import logging
import secrets
from app.config import settings
from app.db import r

logger = logging.getLogger(__name__)


def create_session(username: str):
    sid = secrets.token_urlsafe(32)
    key = f"session:{sid}"
    payload = {"username": username}
    r.setex(key, settings.SESSION_TTL_SECONDS, json.dumps(payload))
    return sid


def get_session(sid: str):
    if not sid:
        return None

    try:
        data = r.get(f"session:{sid}")
    except Exception:
        logger.exception("auth.session.fetch_failed")
        return None

    if not data:
        return None

    try:
        session = json.loads(data)
    except (TypeError, json.JSONDecodeError):
        logger.warning("auth.session.invalid_payload")
        return None

    if not isinstance(session, dict) or "username" not in session:
        logger.warning("auth.session.invalid_shape")
        return None

    return session


def destroy_session(sid: str):
    if sid:
        try:
            r.delete(f"session:{sid}")
        except Exception:
            logger.exception("auth.session.destroy_failed")