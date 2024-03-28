from typing import Annotated, Literal, Dict, Any

from fastapi import APIRouter, Security

from src.llm_provider.moonshot import MoonshotProvider
from src.llm_provider.openai import OpenAIProvider
from src.router.account import User, get_current_active_user
from src.scenario.conclude_wxmp_article import conclude_wxmp_article
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
    return OpenAIProvider.call(**body.dict())


@llm_router.post('/moonshot/call')
@error_handler
async def call_moonshot(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    *,
    body: MoonshotBody,
):
    return MoonshotProvider.call(**body.dict())


@llm_router.get('/{provider}/stat')
async def check_llm_provider_stat(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    return 'chatgpt'


@llm_router.post('/scenario/{name}')
async def check_llm_provider_stat(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    name: Literal["conclude-wxmp-article", ""],
    args: Dict[str, Any]
):
    if name == "conclude-wxmp-article":
        return conclude_wxmp_article(args["url"])
    
    return 'fallback'


@llm_router.get('/{provider}/balance')
async def check_llm_provider_balance(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    return 'chatgpt'
