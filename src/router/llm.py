import asyncio
from typing import Annotated, List, Literal
from typing import Optional

from fastapi import APIRouter, Security, Form, Query, Response
from sse_starlette.sse import EventSourceResponse

from packages.common.pydantic import BaseModel
from packages.common.svg2image import extract_svgs, svg_to_bytes
from packages.fastapi.standard_error import standard_error_handler
from packages.llm.agent.call_agent import call_agent
from packages.llm.agent.call_llm import call_llm
from packages.llm.agent.schema import AgentType
from packages.llm.providers.openai import OpenAIProvider
from packages.llm.schema import ModelType, IMessage
from src.router.account import User, get_current_active_user

llm_router = APIRouter(prefix='/llm', tags=['LLM'])


class ILLMBody(BaseModel):
    messages: List[IMessage]
    model: ModelType
    top_p: Optional[float] = None
    temperature: Optional[float] = None


@llm_router.post('/base')
@standard_error_handler()
async def call_llm_(
    body: ILLMBody
):
    return call_llm(body.messages, body.model, body.top_p, body.temperature)


@llm_router.post('/agent')
@standard_error_handler()
async def call_agent_(
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    input: Annotated[str, Form()],
    agent_type: Annotated[AgentType, Form()] = "default",
    llm_model_type: Optional[ModelType] = Form(description="覆盖配置中的model", default=None, ),
    stream_delay: Optional[float] = None, ):
    stream = stream_delay is not None
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


@llm_router.get('/totem/gen')
@standard_error_handler()
async def gen_totem(
    name: str,
    stream_delay: Optional[float] = Query(None, description="None: 不流；数字: 流间隔（秒）"),
    format: Literal["string", "png"] = Query('png', description="stream 条件下 format 始终为 string"),
    ppi: int = 300,
    width: int = 320
):
    try:
        response = await call_agent_(input=name,
                                     agent_type="totem-gen",
                                     llm_model_type="claude-3-5-sonnet-20240620",
                                     stream_delay=stream_delay)

        if stream_delay is not None or format == "string":
            return response

        # Extract the SVG content from the response
        if isinstance(response, str):
            svg_content = response
        else:
            svg_content = response.content[0].text if hasattr(response, 'content') else str(response)

        if svgs := extract_svgs(svg_content):
            try:
                svg = svgs[0]
                print("[gen_totem] svg: ", svg)
                image_bytes = svg_to_bytes(svg, ppi, format, width=width)
                print('[gen_totem] generated bytes.')
                media_type = {
                    'png': 'image/png',
                    'pdf': 'application/pdf',
                    'ps': 'application/postscript'}.get(format.lower(), 'application/octet-stream')

                return Response(content=image_bytes.getvalue(),
                                media_type=media_type,
                                headers={'Content-Disposition': f'attachment; filename="image.{format}"'})
            except Exception as e:
                return {"error": f"Failed to convert SVG to image: {str(e)}"}
        return {"error": "No SVG found in the content"}
    except Exception as e:
        return {"error": f"Failed to generate totem: {str(e)}"}


@llm_router.get('/openai/list-models')
@standard_error_handler()
async def list_models(  # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    return OpenAIProvider().client.models.list()


class QueryPromptModel(BaseModel):
    query: str


@llm_router.get('/{provider}/stat', description='todo')
@standard_error_handler()
async def check_llm_provider_stat(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])], ):
    return 'chatgpt'


@llm_router.get('/{provider}/balance', description='todo')
@standard_error_handler()
async def check_llm_provider_balance(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])], ):
    return 'chatgpt'
