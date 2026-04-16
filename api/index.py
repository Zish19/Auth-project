"""
Vercel Python Serverless Function entry point.

Wraps the FastAPI application with Mangum so Vercel can invoke it as an
AWS-Lambda-compatible ASGI handler.
"""
import logging
from mangum import Mangum
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.config import settings
from app.routes.auth import router as auth_router

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path-stripping middleware
# ---------------------------------------------------------------------------
# Vercel may forward the request with various path prefixes depending on how
# it constructs the Lambda event. We strip any known prefix so FastAPI always
# sees the clean route (e.g. /auth/register).

_STRIP_PREFIXES = ["/api/backend", "/api/index", "/api"]


class StripBasePath(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path: str = request.scope["path"]
        for prefix in _STRIP_PREFIXES:
            if path == prefix or path.startswith(prefix + "/"):
                stripped = path[len(prefix):] or "/"
                logger.debug("StripBasePath: %s → %s", path, stripped)
                request.scope["path"] = stripped
                # Also fix raw_path so request.url stays consistent
                request.scope["raw_path"] = stripped.encode()
                break
        return await call_next(request)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(StripBasePath)

# Allow the Next.js frontend (same origin on Vercel, or localhost in dev) to
# send cookies / credentials.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/")
def root():
    return {"status": "ok", "app": settings.APP_NAME}


# ---------------------------------------------------------------------------
# Vercel handler
# ---------------------------------------------------------------------------

# Mangum adapts ASGI → AWS Lambda / Vercel's serverless runtime.
handler = Mangum(app, lifespan="off")
