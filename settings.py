from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.path import PROJECT_PATH


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
        },
        {
            "name": "LLM",
        },
        {
            "name": "WeChat",
            "description": "todo: multi-accounts"
        },
        {
            "name": "Spider",
        },
        {
            "name": "OSS",
            "description": "todo"
        },
        {
            "name": "default",
        }
    ]
    
    # LLM
    MOONSHOT_API_KEY: str
    OPENAI_API_KEY: str
    ZHIPU_API_KEY: str
    MINIMAX_API_KEY: str
    MINIMAX_GROUP_ID: str
    
    # APP
    FRONTEND_BASEURL: str
    
    # Wechaty
    WECHATY_PUPPET: str
    WECHATY_PUPPET_SERVICE_ENDPOINT: str
    WECHATY_PUPPET_SERVICE_TOKEN: str
    
    model_config = SettingsConfigDict(env_file=PROJECT_PATH.joinpath(".env"))


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
