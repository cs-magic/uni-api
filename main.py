from fastapi import FastAPI

from settings import Settings
from src.router import root_router
from src.wechat.uni_parser_bot import bot

settings = Settings()

app = FastAPI(
    title=settings.app_title,
    description=settings.description,
    openapi_tags=settings.tags,
    version=settings.version,
)

app.include_router(root_router)


@app.on_event("startup")
async def startup_event():
    # ref: https://chat.openai.com/c/e5ad0da5-7e39-4ad4-9bed-ca94a5456d82
    import asyncio
    asyncio.create_task(bot.start())


@app.on_event("shutdown")
async def shutdown_event():
    await bot.stop()


@app.get("/")
async def read_system_status():
    return {"status": "ok"}
