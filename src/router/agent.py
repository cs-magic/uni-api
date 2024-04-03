from typing import Literal, Annotated, Optional

import yaml
from fastapi import APIRouter, Form
from loguru import logger
from pydantic import BaseModel

from src.llm.utils import get_provider
from src.schema import ModelType
from src.utils.compress_content import compress_content
from src.utils.error_handler import error_handler
from src.utils.path import AGENTS_PATH

agent_router = APIRouter(prefix='/agent', tags=["Agent"])


class AgentConfig(BaseModel):
    name: Optional[str] = "untitled"
    author: Optional[str]
    version: Optional[str]
    model: Optional[ModelType] = "gpt-3.5-turbo"
    total_tokens: int = 8192
    system_prompt: Optional[str]


@agent_router.post('/call')
@error_handler
async def call_agent(
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    content: Annotated[str, Form()],
    agent_type: Annotated[Literal["default", "summariser"], Form()] = "default",
    model_type: Annotated[ModelType, Form(description="覆盖配置中的model")] = None,
):
    with open(AGENTS_PATH.joinpath(f"{agent_type}.agent.yml")) as f:
        agent = AgentConfig.parse_obj(yaml.safe_load(f))
    
    model = model_type if model_type else agent.model
    
    messages = []
    if agent.system_prompt:
        messages.append({
            "role": "system",
            "content": agent.system_prompt,
        })
    
    max_content_len = (
        agent.total_tokens
        - len(agent.system_prompt)  # 系统prompt的长度
        - 1e3  # 输出的预留长度
        - 1e2  # 误差
    )
    content = compress_content(content, max_content_len)
    
    messages.append({
        "role": "user",
        "content": content
    })
    
    logger.debug(f">> calling LLM: Agent={agent}, Messages={messages}")
    res = get_provider(model).call(
        model=model,
        messages=messages,
        top_p=0.03,  # ref: https://platform.openai.com/docs/api-reference/chat/create
        # temperature=0
    )
    logger.debug(f"<< result: {res}")
    return {
        "model": model,
        "content": res.choices[0].message.content
    }
