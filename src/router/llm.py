import asyncio
from typing import Annotated, List
from typing import Optional

from fastapi import APIRouter, Security, Form, Request
from sse_starlette.sse import EventSourceResponse

from packages.common_common.pydantic import BaseModel
from packages.common_fastapi.error_handler import error_handler
from packages.common_llm.agent.call_agent import call_agent
from packages.common_llm.agent.call_llm import call_llm
from packages.common_llm.agent.schema import AgentType
from packages.common_llm.providers.openai import OpenAIProvider
from packages.common_llm.schema import ModelType, IMessage
from src.router.account import User, get_current_active_user

llm_router = APIRouter(prefix='/llm', tags=['LLM'])


class ILLMBody(BaseModel):
    messages: List[IMessage]
    model: ModelType
    top_p: Optional[float] = None
    temperature: Optional[float] = None


@llm_router.post('/base')
@error_handler
async def call_llm_(
    body: ILLMBody
):
    return call_llm(body.messages, body.model, body.top_p, body.temperature)


@llm_router.post('/agent')
@error_handler
async def call_agent_(
    request: Request,
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    input: Annotated[str, Form()],
    agent_type: Annotated[AgentType, Form()] = "default",
    llm_model_type: Optional[ModelType] = Form(description="覆盖配置中的model", default=None, ),
    stream: bool = False,
    stream_delay: int = 0, ):
    result = call_agent(input, agent_type, llm_model_type, stream=stream)

    if not stream:
        return result

    async def event_generator():
        for item in result:
            yield {"event": "token", "id": "message_id", "data": item, }
            await asyncio.sleep(stream_delay)
        else:
            yield {"event": "end"}

    return EventSourceResponse(event_generator())


@llm_router.get('/openai/list-models')
@error_handler
async def list_models(  # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    return OpenAIProvider().client.models.list()


class QueryPromptModel(BaseModel):
    query: str


@llm_router.get('/{provider}/stat', description='todo')
@error_handler
async def check_llm_provider_stat(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])], ):
    return 'chatgpt'


@llm_router.get('/{provider}/balance', description='todo')
@error_handler
async def check_llm_provider_balance(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])], ):
    return 'chatgpt'
