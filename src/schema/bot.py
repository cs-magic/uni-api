from packages.common_general.pydantic import BaseModel


class BotStatus(BaseModel):
    version: str
    features_enabled: bool
    llm_enabled: bool
    alive_time: str


class BotSettings(BaseModel):
    help: str
    shelp: str
    status: str
