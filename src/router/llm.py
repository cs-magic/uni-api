from typing import Annotated

from fastapi import APIRouter, Security
from pydantic import BaseModel

from src.llm.providers.openai import OpenAIProvider
from src.router.account import User, get_current_active_user
from packages.common_fastapi.error_handler import error_handler

llm_router = APIRouter(prefix='/llm', tags=['LLM'])


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
