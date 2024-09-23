import os.path
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.responses import FileResponse

from packages.common_fastapi.dum_openapi import dump_openapi
from settings import settings
from src.router import root_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown


app = FastAPI(
    title=settings.app_title,
    description=settings.description,
    openapi_tags=settings.tags,
    version=settings.version,
    lifespan=lifespan
)

app.include_router(root_router)


@app.get("/")
async def read_system_status():
    return {"status": "ok"}


@app.get("/openapi")
async def get_openapi():
    return FileResponse(os.path.join(__file__, "../openapi.json"))


dump_openapi(app)

if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)