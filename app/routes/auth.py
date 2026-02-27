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
    get_challenge,
    mark_challenge_used
)
from app.services.session_service import (
    create_session,
    get_session,
    destroy_session
)
from app.crypto.verify import verify_proof
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

USERS = {}


@router.post("/register", response_model=MessageResponse)
def register(body: RegisterRequest):
    if body.username in USERS:
        raise HTTPException(status_code=409, detail="Username already exists")

    USERS[body.username] = body.public_key
    return {"message": "User registered"}


@router.post("/login/challenge", response_model=LoginChallengeResponse)
def login_challenge(body: LoginChallengeRequest):
    if body.username not in USERS:
        raise HTTPException(status_code=404, detail="User not found")

    challenge_id, challenge = create_challenge(body.username)

    return {
        "challenge_id": challenge_id,
        "challenge": challenge,
        "expires_in": settings.CHALLENGE_TTL_SECONDS
    }
def login_challenge(body: LoginChallengeRequest):
    if body.username not in USERS:
        raise HTTPException(status_code=404, detail="User not found")

    challenge_id, challenge = create_challenge(body.username)

    return {
        "challenge_id": challenge_id,
        "challenge": challenge,
        "expires_in": settings.CHALLENGE_TTL_SECONDS
    }


@router.post("/login/verify", response_model=MessageResponse)
def login_verify(body: LoginVerifyRequest, response: Response):
    user_pk = USERS.get(body.username)
    if not user_pk:
        raise HTTPException(status_code=404, detail="User not found")

    ch = get_challenge(body.challenge_id)
    if not ch:
        raise HTTPException(status_code=400, detail="Invalid or expired challenge")

    if ch["used"]:
        raise HTTPException(status_code=400, detail="Challenge already used")

    if ch["username"] != body.username:
        raise HTTPException(status_code=400, detail="Challenge-user mismatch")

    ok = verify_proof(user_pk, ch["challenge"], body.R, body.s)
    if not ok:
        raise HTTPException(status_code=401, detail="Invalid proof")

    mark_challenge_used(body.challenge_id)
    sid = create_session(body.username)

    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=sid,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE
    )

    return {"message": "Login success"}


@router.post("/logout", response_model=MessageResponse)
def logout(request: Request, response: Response):
    sid = request.cookies.get(settings.COOKIE_NAME)
    destroy_session(sid)
    response.delete_cookie(settings.COOKIE_NAME)

    return {"message": "Logged out"}


@router.get("/me")
def me(request: Request):
    sid = request.cookies.get(settings.COOKIE_NAME)
    session = get_session(sid)

    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {"username": session["username"]}