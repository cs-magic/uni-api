from typing import Annotated

import yaml
from fastapi import APIRouter, Security, Form
from loguru import logger
from pydantic import BaseModel

from packages.common_algo.string import compress_content
from packages.common_fastapi.error_handler import error_handler
from src.agent.schema import AgentType, AgentConfig
from src.llm.providers.openai import OpenAIProvider
from src.llm.utils import get_provider
from src.path import AGENT_CONFIG_PATH
from src.router.account import User, get_current_active_user
from src.schema import ModelType

llm_router = APIRouter(prefix='/llm', tags=['LLM'])


@llm_router.post('/agent')
@error_handler
async def call_agent(
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    input: Annotated[str, Form()],
    agent_type: Annotated[AgentType, Form()] = "default",
    llm_model_type: Annotated[ModelType, Form(description="覆盖配置中的model")] = "gpt-3.5-turbo",
):
    logger.info('-- calling agent...')
    with open(AGENT_CONFIG_PATH.joinpath(f"{agent_type}.agent.yml")) as f:
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
    content = compress_content(input, max_content_len)
    
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
    return res.choices[0].message.content


@llm_router.get('/openai/list-models')
@error_handler
async def query_openai(
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    return OpenAIProvider().client.models.list()


class QueryPromptModel(BaseModel):
    query: str


@llm_router.get('/{provider}/stat', summary='todo')
@error_handler
async def check_llm_provider_stat(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    return 'chatgpt'


@llm_router.get('/{provider}/balance', summary='todo')
@error_handler
async def check_llm_provider_balance(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    return 'chatgpt'
