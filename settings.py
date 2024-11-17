from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict

from path import PROJECT_PATH


class Settings(BaseSettings):
    app_name: str = "uni-api"
    version: str = "0.5.0"
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
    tags: Any = [{"name": "Account", }, {"name": "LLM", }, {"name": "Spider", }, {"name": "OSS", "description": "todo"},
                 {"name": "Cases", }, {"name": "Rama", }, {"name": "default", }, ]

    DATABASE_URL: str
    DATABASE_BACKEND_URL: str

    # LLM
    MOONSHOT_API_KEY: str
    OPENAI_API_KEY: str
    ZHIPU_API_KEY: str
    MINIMAX_API_KEY: str
    MINIMAX_GROUP_ID: str
    DASHSCOPE_API_KEY: str
    DOUBAO_AK: str
    DOUBAO_SK: str
    DOUBAO_API_KEY: str
    ANTHROPIC_API_KEY: str

    # auth
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    wechat_app_id: str = ""
    wechat_app_secret: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""

    # payment
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str

    # others
    FRONTEND_BASEURL: str

    model_config = SettingsConfigDict(env_file=PROJECT_PATH.joinpath(".env"), extra="ignore")


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
