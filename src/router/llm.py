from typing import Annotated

from fastapi import APIRouter, Security

from src.llm_provider.base import LLMProvider
from src.router.account import User, get_current_active_user
from src.schema import OpenAIBody, MoonshotBody
from src.utls.error_handler import error_handler

llm_router = APIRouter(prefix='/llm', tags=['LLM'])


@llm_router.post('/openai/call')
@error_handler
async def call_openai(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    *,
    body: OpenAIBody,
):
    return LLMProvider("openai").call(**body.dict())


@llm_router.post('/moonshot/call')
@error_handler
async def call_moonshot(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    *,
    body: MoonshotBody,
):
    return LLMProvider("moonshot").call(**body.dict())


@llm_router.get('/{provider}/stat')
async def check_llm_provider_stat(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    return 'chatgpt'


@llm_router.get('/{provider}/balance')
async def check_llm_provider_balance(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    return 'chatgpt'
