import json
import os.path
from cgi import logfp
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Response
from starlette.datastructures import MutableHeaders
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import FileResponse, StreamingResponse, JSONResponse
from starlette.types import ASGIApp

from packages.common_fastapi.dum_openapi import dump_openapi
from settings import settings
from src.router import root_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown

class PreserveHeaderCaseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # response.headers['Date2'] = response.headers['Date'].capitalize()
        print("response headers: ", response.headers)

        return response

app = FastAPI(
    title=settings.app_title,
    description=settings.description,
    openapi_tags=settings.tags,
    version=settings.version,
    lifespan=lifespan
)
app.add_middleware(GZipMiddleware)
app.add_middleware(PreserveHeaderCaseMiddleware)

app.include_router(root_router)


@app.get("/")
async def read_system_status():
    return {"status": "ok"}


@app.get("/openapi")
async def get_openapi():
    return FileResponse(os.path.join(__file__, "../openapi.json"))


dump_openapi(app)

if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", port=8000, reload=True, server_header=False, date_header=False)