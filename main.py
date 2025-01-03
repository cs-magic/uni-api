import os.path
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from apitally.fastapi import ApitallyMiddleware

from packages.fastapi.dump_openapi import dump_openapi
from settings import settings
from router import root_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield  # shutdown


app = FastAPI(title=settings.app_title,
              description=settings.description,
              # openapi_tags=settings.tags,
              version=settings.version,
              lifespan=lifespan)

app.include_router(root_router)

origins = ["*"]

app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"], )

# ref: [App setup instructions - Apitally](https://app.apitally.io/apps/uni-api/setup)
app.add_middleware(
    ApitallyMiddleware,
    client_id="a89ca501-a269-4fdd-9de8-e7bd3432f8ef",
    env="prod",  # or "dev"
)

@app.get("/")
async def read_system_status():
    return {"status": "ok"}


@app.get("/openapi")
async def get_openapi():
    return FileResponse(os.path.join(__file__, "../openapi.json"))


dump_openapi(app)

if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", port=8000, reload=True, server_header=False, date_header=False)
