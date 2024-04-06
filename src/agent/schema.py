from typing import Optional, Literal

from packages.common_general.pydantic import BaseModel
from src.schema import ModelType


class AgentConfig(BaseModel):
    name: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None
    model: Optional[ModelType] = "gpt-3.5-turbo"
    total_tokens: Optional[int] = 8192
    system_prompt: Optional[str] = None


AgentType = Literal["default", "summarize-content"]
