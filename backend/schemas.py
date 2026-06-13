from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    public_key: str = Field(min_length=1, max_length=2048)

    @field_validator("username", "public_key", mode="before")
    @classmethod
    def strip_fields(cls, value: str) -> str:
        return value.strip()


class LoginChallengeRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)

    @field_validator("username", mode="before")
    @classmethod
    def strip_username(cls, value: str) -> str:
        return value.strip()


class LoginChallengeResponse(BaseModel):
    challenge_id: str
    challenge: str
    expires_in: int


class LoginVerifyRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    challenge_id: str = Field(min_length=8, max_length=256)
    R: str = Field(min_length=1, max_length=4096)
    s: str = Field(min_length=1, max_length=4096)

    @field_validator("username", "challenge_id", "R", "s", mode="before")
    @classmethod
    def strip_verify_fields(cls, value: str) -> str:
        return value.strip()


class MessageResponse(BaseModel):
    message: str