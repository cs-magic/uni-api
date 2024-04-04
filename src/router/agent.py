from typing import Literal, Annotated, Optional

import yaml
from fastapi import APIRouter, Form
from loguru import logger
from pydantic import BaseModel

from src.llm.utils import get_provider
from src.schema import ModelType
from packages.common_algo.string import compress_content
from packages.common_fastapi.error_handler import error_handler
from src.path import AGENTS_PATH

agent_router = APIRouter(prefix='/agent', tags=["Agent"])


class AgentConfig(BaseModel):
    name: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None
    model: Optional[ModelType] = "gpt-3.5-turbo"
    total_tokens: Optional[int] = 8192
    system_prompt: Optional[str] = None


AgentType = Literal["default", "summarize-content"]


def call_agent_base(content: str, agent_type: AgentType = None, llm_model_type: ModelType = "gpt-3.5-turbo"):
    logger.info('-- calling agent...')
    with open(AGENTS_PATH.joinpath(f"{agent_type}.agent.yml")) as f:
        agent = AgentConfig.parse_obj(yaml.safe_load(f))
    
    model = llm_model_type if llm_model_type else agent.model
    
    system_prompt = agent.system_prompt or ""
    messages = []
    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt,
        })
    
    max_content_len = (
        agent.total_tokens
        - len(system_prompt)  # 系统prompt的长度
        - 1e3  # 输出的预留长度
        - 1e2  # 误差
    )
    content = compress_content(content, max_content_len)
    
    messages.append({
        "role": "user",
        "content": content
    })
    
    logger.info(f">> calling LLM: Agent={agent}, Messages={messages}")
    res = get_provider(model).call(
        model=model,
        messages=messages,
        top_p=0.03,  # ref: https://platform.openai.com/docs/api-reference/chat/create
        # temperature=0
    )
    logger.info(f"<< result: {res}")
    return {
        "model": model,
        "content": res.choices[0].message.content
    }


@agent_router.post('/call')
@error_handler
async def call_agent(
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    input: Annotated[str, Form()],
    agent_type: Annotated[AgentType, Form()] = "default",
    llm_model_type: Annotated[ModelType, Form(description="覆盖配置中的model")] = "gpt-3.5-turbo",
):
    data = call_agent_base(input, agent_type, llm_model_type)
    return data
