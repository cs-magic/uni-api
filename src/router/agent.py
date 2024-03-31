from typing import Literal, Annotated, Optional

import yaml
from fastapi import APIRouter, Form
from loguru import logger
from pydantic import BaseModel

from src.llm.utils import get_provider
from src.schema import ModelType
from src.utls.path import AGENTS_PATH

agent_router = APIRouter(prefix='/agent', tags=["Agent"])


class AgentConfig(BaseModel):
    name: Optional[str] = "untitled"
    author: Optional[str]
    version: Optional[str]
    model: Optional[ModelType] = "gpt-3.5-turbo"
    system_prompt: Optional[str]


@agent_router.post('/call')
async def call_agent(
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    content: Annotated[str, Form()],
    agent_type: Annotated[Literal["default", "summariser"], Form()] = "default"
):
    with open(AGENTS_PATH.joinpath(f"{agent_type}.agent.yml")) as f:
        agent = AgentConfig.parse_obj(yaml.safe_load(f))
    
    model = agent.model
    
    messages = []
    if agent.system_prompt:
        messages.append({
            "role": "system",
            "content": agent.system_prompt,
        })
    
    # ref: https://chat.openai.com/c/f8fa5a99-f1f0-441d-a883-903118efa838
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
    print("\n------\n", res.choices[0].message.content)
    return res
