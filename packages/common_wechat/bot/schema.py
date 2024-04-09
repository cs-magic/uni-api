from packages.common_common.pydantic import BaseModel
from packages.common_llm.schema import ModelType


class BotStatus(BaseModel):
    version: str
    features_enabled: bool
    summary_model: ModelType | None
    alive_time: str


class BotSettings(BaseModel):
    help: str
    shelp: str
    status: str
