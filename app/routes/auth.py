import logging
from fastapi import APIRouter, HTTPException, Response, Request
from app.schemas import (
    RegisterRequest,
    LoginChallengeRequest,
    LoginChallengeResponse,
    LoginVerifyRequest,
    MessageResponse
)
from app.services.challenge_service import (
    create_challenge,
)
from app.services.session_service import (
    get_session,
    destroy_session
)
from app.services.auth_service import verify_login_attempt
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

USERS = {}


@router.post("/register", response_model=MessageResponse)
def register(body: RegisterRequest):
    if body.username in USERS:
        raise HTTPException(status_code=409, detail="Username already exists")

    USERS[body.username] = body.public_key
    logger.info("auth.register.success", extra={"username": body.username})
    return {"message": "User registered"}


@router.post("/login/challenge", response_model=LoginChallengeResponse)
def login_challenge(body: LoginChallengeRequest):
    if body.username not in USERS:
        logger.warning("auth.challenge.user_missing", extra={"username": body.username})
        raise HTTPException(status_code=404, detail="User not found")

    challenge_id, challenge = create_challenge(body.username)
    logger.info(
        "auth.challenge.created",
        extra={"username": body.username, "challenge_id": challenge_id},
    )

    return {
        "challenge_id": challenge_id,
        "challenge": challenge,
        "expires_in": settings.CHALLENGE_TTL_SECONDS
    }


@router.post("/login/verify", response_model=MessageResponse)
def login_verify(body: LoginVerifyRequest, response: Response):
    user_pk = USERS.get(body.username)
    if not user_pk:
        logger.warning("auth.verify.user_missing", extra={"username": body.username})
        raise HTTPException(status_code=404, detail="User not found")

    sid = verify_login_attempt(
        username=body.username,
        user_public_key=user_pk,
        challenge_id=body.challenge_id,
        R=body.R,
        s=body.s,
    )

    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=sid,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )

    return {"message": "Login success"}


@router.post("/logout", response_model=MessageResponse)
def logout(request: Request, response: Response):
    sid = request.cookies.get(settings.COOKIE_NAME)
    destroy_session(sid)
    response.delete_cookie(settings.COOKIE_NAME)
    logger.info("auth.logout.success")

    return {"message": "Logged out"}


@router.get("/me")
def me(request: Request):
    sid = request.cookies.get(settings.COOKIE_NAME)
    session = get_session(sid)

    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {"username": session["username"]}