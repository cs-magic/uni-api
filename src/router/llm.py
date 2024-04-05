from typing import Annotated

from fastapi import APIRouter, Security, Form
from pydantic import BaseModel

from packages.common_fastapi.error_handler import error_handler
from src.agent.core import call_agent
from src.agent.schema import AgentType
from src.llm.providers.openai import OpenAIProvider
from src.router.account import User, get_current_active_user
from src.schema import ModelType

llm_router = APIRouter(prefix='/llm', tags=['LLM'])


@llm_router.post('/agent')
@error_handler
async def call_agent_route(
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    input: Annotated[str, Form()],
    agent_type: Annotated[AgentType, Form()] = "default",
    llm_model_type: Annotated[ModelType, Form(description="覆盖配置中的model")] = "gpt-3.5-turbo",
):
    data = call_agent(input, agent_type, llm_model_type)
    return data


@llm_router.get('/openai/list-models')
@error_handler
async def call_openai(
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
