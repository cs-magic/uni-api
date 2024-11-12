from typing import Optional, Literal, List


from packages.common.pydantic import BaseModel
from packages.llm.providers._base import M
from packages.llm.schema import OpenAIMessages


class AgentConfig(BaseModel):
    name: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None
    model: Optional[M] = "gpt-3.5-turbo"
    total_tokens: Optional[int] = 8192
    max_token_output: Optional[int] = None
    system_prompt: Optional[str] = None
    # todo: general chat type
    context: OpenAIMessages = []

    class Config:
        arbitrary_types_allowed = True


AgentType = Literal["default", "summarize-content", "summarize-poem", "totem-gen"]
