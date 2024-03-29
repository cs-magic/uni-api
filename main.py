from fastapi import FastAPI

from settings import Settings
from src.router import root_router

settings = Settings()

app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    openapi_tags=settings.tags,
    version=settings.version,
)

app.include_router(root_router)


@app.get("/")
async def read_system_status():
    return {"status": "ok"}
