import logging
from fastapi import HTTPException, status

from app.config import settings
from app.crypto.verify import ProofFormatError, verify_proof
from app.services.challenge_service import get_challenge, mark_challenge_used
from app.services.session_service import create_session

logger = logging.getLogger(__name__)


def verify_login_attempt(*, username: str, user_public_key: str, challenge_id: str, R: str, s: str) -> str:
    logger.info(
        "auth.verify.started",
        extra={"username": username, "challenge_id": challenge_id},
    )

    challenge = get_challenge(challenge_id)
    if not challenge:
        logger.warning(
            "auth.verify.challenge_missing",
            extra={"username": username, "challenge_id": challenge_id},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired challenge",
        )

    if challenge.get("used") is True:
        logger.warning(
            "auth.verify.challenge_used",
            extra={"username": username, "challenge_id": challenge_id},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Challenge already used",
        )

    if challenge.get("username") != username:
        logger.warning(
            "auth.verify.challenge_username_mismatch",
            extra={"username": username, "challenge_id": challenge_id},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Challenge-user mismatch",
        )

    if settings.AUTH_MODE == "dev_bypass":
        logger.warning(
            "auth.verify.dev_bypass_enabled",
            extra={"username": username, "challenge_id": challenge_id},
        )
    else:
        try:
            is_valid = verify_proof(
                user_public_key,
                challenge.get("challenge", ""),
                R,
                s,
            )
        except ProofFormatError as exc:
            logger.warning(
                "auth.verify.invalid_proof_format",
                extra={"username": username, "challenge_id": challenge_id},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        except Exception as exc:
            logger.exception(
                "auth.verify.unexpected_error",
                extra={"username": username, "challenge_id": challenge_id},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to verify proof",
            ) from exc

        if not is_valid:
            logger.warning(
                "auth.verify.invalid_proof",
                extra={"username": username, "challenge_id": challenge_id},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid proof",
            )

    if not mark_challenge_used(challenge_id):
        logger.exception(
            "auth.verify.challenge_mark_failed",
            extra={"username": username, "challenge_id": challenge_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update challenge state",
        )

    try:
        session_id = create_session(username)
    except Exception as exc:
        logger.exception(
            "auth.verify.session_creation_failed",
            extra={"username": username, "challenge_id": challenge_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create session",
        ) from exc

    logger.info(
        "auth.verify.session_created",
        extra={"username": username, "challenge_id": challenge_id},
    )
    return session_id
