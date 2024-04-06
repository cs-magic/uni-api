from packages.common_general.pydantic import BaseModel
from src.schema.llm import ModelType


class BotStatus(BaseModel):
    version: str
    features_enabled: bool
    summary_model: ModelType | None
    alive_time: str


class BotSettings(BaseModel):
    help: str
    shelp: str
    status: str
