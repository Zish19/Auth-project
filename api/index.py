"""
Vercel Python Serverless Function entry point.

Wraps the FastAPI application with Mangum so Vercel can invoke it as an
AWS-Lambda-compatible ASGI handler.
"""
from mangum import Mangum
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.auth import router as auth_router

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title=settings.APP_NAME, root_path="/api/backend")

# Allow the Next.js frontend (same origin on Vercel, or localhost in dev) to
# send cookies / credentials.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        # Set ALLOWED_ORIGIN in Vercel env vars to your production domain.
        # e.g. https://your-project.vercel.app
    ],
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
