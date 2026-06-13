import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = "zk-session-auth"
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "900"))
    CHALLENGE_TTL_SECONDS = int(os.getenv("CHALLENGE_TTL_SECONDS", "60"))
    COOKIE_NAME = "sid"
    COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")
    AUTH_MODE = os.getenv("AUTH_MODE", "dev_bypass").lower()


settings = Settings()