from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.utils.path import PROJECT_PATH


class Settings(BaseSettings):
    app_name: str = "uni-api"
    version: str = "0.1.3"
    admin_email: str = "shawninjuly@gmail.com"
    
    @property
    def repo(self):
        return f"https://github.com/cs-magic/{self.app_name}"
    
    @property
    def app_title(self):
        return " ".join([i.capitalize() for i in self.app_name.split("-")])
    
    @property
    def description(self):
        return f"聚合AGI行业的主流API，提供动态key管理、算法调度、前端监控、可扩展性配置等功能 （opensource: {self.repo}）"
    
    # ref: https://fastapi.tiangolo.com/tutorial/metadata/#metadata-for-tags
    tags: Any = [
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
            "name": "Agent",
            "description": "场景相关 API"
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
    
    MOONSHOT_API_KEY: str
    OPENAI_API_KEY: str
    ZHIPU_API_KEY: str
    MINIMAX_API_KEY: str
    MINIMAX_GROUP_ID: str
    
    model_config = SettingsConfigDict(env_file=PROJECT_PATH.joinpath(".env"))


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
