from fastapi import FastAPI

from src.router import root_router

# ref: https://fastapi.tiangolo.com/tutorial/metadata/#metadata-for-tags
tags_metadata = [
    {
        "name": "Account",
        "description": "账号相关 API （基于 OAuth2 / HTTP Basic）",
    },
    {
        "name": "LLM",
        "description": "大语言模型相关 API",
        "externalDocs": {
            "description": "外部文档参考",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
    {
        "name": "Common",
        "description": "一些通用 API（例如OSS相关的）"
    },
    {
        "name": "default",
        "description": "待分类/默认 API"
    }
]

app = FastAPI(
    title="Open API",
    description="聚合AGI行业的主流API，提供动态key管理、算法调度、前端监控、可扩展性配置等功能",
    openapi_tags=tags_metadata,
)

app.include_router(root_router)


@app.get("/")
async def read_system_status():
    return {"status": "ok"}
