from typing import Annotated

import openai
from fastapi import APIRouter, Security
from openai import OpenAI
from pydantic import BaseModel

from src.llm.providers.moonshot import MoonshotProvider
from src.llm.providers.openai import OpenAIProvider
from src.router.account import User, get_current_active_user
from src.schema import OpenAIBody, MoonshotBody
from src.utils.error_handler import error_handler

llm_router = APIRouter(prefix='/llm', tags=['LLM'])


@llm_router.post('/openai/call')
@error_handler
async def call_openai(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    *,
    body: OpenAIBody,
):
    return OpenAIProvider.call(**body.dict())


@llm_router.get('/openai/list-models')
@error_handler
async def call_openai(
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    return OpenAIProvider().client.models.list()


@llm_router.post('/moonshot/call')
@error_handler
async def call_moonshot(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    *,
    body: MoonshotBody,
):
    return MoonshotProvider.call(**body.dict())


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
