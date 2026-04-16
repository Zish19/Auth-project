"""
Vercel Python Serverless Function entry point.

Wraps the FastAPI application with Mangum so Vercel can invoke it as an
AWS-Lambda-compatible ASGI handler.
"""
import os
import sys

# ---------------------------------------------------------------------------
# Ensure the repo root is on sys.path so `from app.xxx import yyy` works
# inside Vercel's Lambda sandbox (the builder only adds api/ by default).
# ---------------------------------------------------------------------------
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

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
# Vercel may forward the request with various path prefixes.
# Strip any known prefix so FastAPI always sees the clean route
# (e.g. /auth/register instead of /api/backend/auth/register).

_STRIP_PREFIXES = ["/api/backend", "/api/index", "/api"]


class StripBasePath(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path: str = request.scope["path"]
        for prefix in _STRIP_PREFIXES:
            if path == prefix or path.startswith(prefix + "/"):
                stripped = path[len(prefix):] or "/"
                request.scope["path"] = stripped
                request.scope["raw_path"] = stripped.encode()
                break
        return await call_next(request)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(StripBasePath)

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

handler = Mangum(app, lifespan="off")
