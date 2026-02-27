from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    public_key: str


class LoginChallengeRequest(BaseModel):
    username: str


class LoginChallengeResponse(BaseModel):
    challenge_id: str
    challenge: str
    expires_in: int


class LoginVerifyRequest(BaseModel):
    username: str
    challenge_id: str
    R: str
    s: str


class MessageResponse(BaseModel):
    message: str