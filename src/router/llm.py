from typing import Annotated

from fastapi import APIRouter, Security

from src.router.account import User, get_current_active_user

llm_router = APIRouter(prefix='/llm', tags=['LLM'])


@llm_router.post('/{provider}/call')
async def call_llm_provider(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    return 'chatgpt'


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
