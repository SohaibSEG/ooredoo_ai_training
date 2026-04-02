from fastapi import FastAPI

from app.core.config import settings
from app.api.routes import auth_router, sessions_router


app = FastAPI(title=settings.app_name)

app.include_router(auth_router)
app.include_router(sessions_router)


@app.get("/health")
def health():
    return {"status": "ok"}
