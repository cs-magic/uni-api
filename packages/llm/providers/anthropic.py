from typing import List, Optional, Iterable, Dict, Union, Literal

import anthropic
import httpx
from openai import NotGiven, NOT_GIVEN
from openai._types import Headers, Query, Body
from openai.types.chat import completion_create_params, ChatCompletionToolChoiceOptionParam, ChatCompletionToolParam

from packages.llm.providers._base import LLMProviderBase, M
from packages.llm.schema import AnthropicModels, IMessage
from packages.llm.utils.openai2anthropic import openai2anthropic
from settings import settings


class AnthropicProvider(LLMProviderBase[AnthropicModels]):
    """
    todo: claude api
    """
    name = "anthropic"
    base_url = None
    api_key = settings.ANTHROPIC_API_KEY

    client = anthropic.Anthropic(# defaults to os.environ.get("ANTHROPIC_API_KEY")
        api_key=api_key, )

    def __init__(self):
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set in environment variables")

    def call(
        self,
        *,
        messages: List[IMessage],
        model: M,
        frequency_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
        functions: Iterable[completion_create_params.Function] | NotGiven = NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | NotGiven = NOT_GIVEN,
        logprobs: Optional[bool] | NotGiven = NOT_GIVEN,
        max_tokens: Optional[int] | NotGiven = None,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        presence_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN,
        seed: Optional[int] | NotGiven = None,
        stop: Union[Optional[str], List[str]] | NotGiven = None,
        stream: Optional[Literal[False]] | Literal[True] | NotGiven = None,
        temperature: Optional[float] | NotGiven = None,
        tool_choice: ChatCompletionToolChoiceOptionParam | NotGiven = None,
        tools: Iterable[ChatCompletionToolParam] | NotGiven = None,
        top_logprobs: Optional[int] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = None,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = None, ):

        # anthropic's system message should be in the param: {'type': 'invalid_request_error', 'message': 'messages: Unexpected role "system". The Messages API accepts a top-level `system` parameter, not "system" as an input message role.'}
        system = None
        if len(messages) > 0 and messages[0].get("role") == "system":
            system = messages[0].get("content")
            messages = messages[1:]

        messages = openai2anthropic(messages)
        # print(f"[anthropic]: ", {"system": system, "messages": messages, "stream": stream})

        message = self.client.messages.create(model=model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
            stream=stream, )
        return message
