from fastapi import FastAPI
from backend.config import settings
from backend.routes.auth import router as auth_router


app = FastAPI(title=settings.APP_NAME)
app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "app": settings.APP_NAME
    }