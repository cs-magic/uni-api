from typing import Literal, Optional, Iterable, Union, List, Dict

import httpx
from openai import NotGiven
from openai.types.chat import completion_create_params, \
    ChatCompletionSystemMessageParam, \
    ChatCompletionUserMessageParam, \
    ChatCompletionAssistantMessageParam, \
    ChatCompletionToolParam, \
    ChatCompletionToolChoiceOptionParam
from pydantic import Field
from typing_extensions import TypedDict

from packages.common.pydantic import BaseModel

ProviderType = Literal["openai", "moonshot", "doubao", "baichuan", "zhipu", "dashscope", "anthropic"]

OpenAIMessageParam = Union[
    ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam,]

OpenAIMessages = Iterable[Dict]


class IMessage(TypedDict):
    content: str | List[Dict]
    role: Literal["system", "user", "assistant"]


class LLMBodyBase(BaseModel):
    """
    todo: json --> openai MAP
    """

    model: str
    messages: List[IMessage]
    frequency_penalty: Optional[float] = None

    logprobs: Optional[bool] = None
    presence_penalty: Optional[float] = None
    response_format: completion_create_params.ResponseFormat = None
    seed: Optional[int] = None
    stop: Union[Optional[str], List[str]] = None
    stream: Optional[Literal[False]] | Literal[True] = None
    temperature: Optional[float] = None
    tool_choice: ChatCompletionToolChoiceOptionParam = None
    tools: Iterable[ChatCompletionToolParam] = None
    top_logprobs: Optional[int] = None
    top_p: Optional[float] = None
    user: str = None

    n: Optional[int] | NotGiven = 1  # 最小要1个，否则会报错
    max_tokens: Optional[int] | NotGiven = Field(4e3,
                                                 description="回复的最大token长度，不可以设置超过模型的长度，3.5-turbo总共最大4096，程序发送时可以直接忽略该字段")
    timeout: float | httpx.Timeout | None = 5000  # N毫秒内响应，否则会 connection error

    logit_bias: Optional[Dict[str, int]] = {}

    ## NOTE: functions deprecated by tools
    # function_call: completion_create_params.FunctionCall = None
    # functions: Iterable[completion_create_params.Function] = None

    ## NOTE: Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    ## The extra values given here take precedence over values defined on the client or passed to this method.
    # extra_headers: Headers | None = None
    # extra_query: Query | None = None,
    # extra_body: Body | None = None,

    class Config:
        arbitrary_types_allowed = True


OpenAIModel = Literal[
    "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0301", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-1106", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-16k-0613", "gpt-4-0125-preview", "gpt-4-turbo-preview", "gpt-4-1106-preview", "gpt-4-vision-preview", "gpt-4", "gpt-4-0314", "gpt-4-0613", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-0613",]


class OpenAIBody(LLMBodyBase):
    model: OpenAIModel


AnthropicModels = Literal['claude-3-5-sonnet-20240620']

MoonshotModel = Literal["moonshot-v1_plain-8k", "moonshot-v1_plain-32k", "moonshot-v1_plain-128k"]

BaichuanModel = Literal["Baichuan2-Turbo", "Baichuan2-Turbo-192k",]

ZhipuModel = Literal["glm-3-turbo", "glm-4",]

MinimaxModel = Literal["abab6-chat", "abab5.5-chat", "abab5.5s-chat"]

DashscopeModel = Literal[  # dashscope.Generation.Models.qwen_turbo,
    'qwen-turbo', 'qwen-plus', 'qwen-max',]

DoubaoModel = Literal[
    "Doubao-lite-4k", "Doubao-lite-32k", "Doubao-lite-128k", "Doubao-pro-4k", "Doubao-pro-32k", "Doubao-pro-128k",]

ModelType = Literal[
    OpenAIModel, MoonshotModel, ZhipuModel, MinimaxModel, DashscopeModel, BaichuanModel, DoubaoModel, AnthropicModels]


class MoonshotBody(LLMBodyBase):
    model: MoonshotModel
