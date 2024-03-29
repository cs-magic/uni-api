from typing import Literal, Annotated

from fastapi import APIRouter, Form
from loguru import logger
from pydantic import BaseModel

from src.llm_provider.utils import get_provider
from src.schema import ModelType
from src.utls.path import AGENTS_PATH

agent_router = APIRouter(prefix='/agent', tags=["Agent"])


class RawBody(BaseModel):
    content: str  # Use bytes if you expect binary data


@agent_router.post('/call')
async def call_agent(
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    content: Annotated[str, Form()],
    
    agent_type: Literal["default", "conclude-article"] = "default",
    model_type: ModelType = "gpt-3.5-turbo",
):
    messages = []
    if agent_type != "default":
        with open(AGENTS_PATH.joinpath(f"{agent_type}.prompt.md")) as f:
            prompt = f.read()
        messages.append({
            "role": "system",
            "content": prompt,
        })
    
    # ref: https://chat.openai.com/c/f8fa5a99-f1f0-441d-a883-903118efa838
    messages.append({
        "role": "user",
        "content": content
    })
    
    logger.info(f">> calling LLM: Model={model_type}, Prompt.name={agent_type}, Messages={messages}")
    res = get_provider(model_type).call(
        model=model_type,
        messages=messages
    )
    logger.info(f"<< result: {res}")
    print("\n------\n", res.choices[0].message.content)
    return res
