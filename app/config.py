import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = "zk-session-auth"
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "900"))
    CHALLENGE_TTL_SECONDS = int(os.getenv("CHALLENGE_TTL_SECONDS", "60"))
    COOKIE_NAME = "sid"
    COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"
    COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")
    AUTH_MODE = os.getenv("AUTH_MODE", "dev_bypass").lower()

    @property
    def ALLOWED_ORIGINS(self):
        origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]


settings = Settings()