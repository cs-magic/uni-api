import dotenv

dotenv.load_dotenv()

from loguru import logger

from packages.llm.schema import ModelType, OpenAIMessages
from packages.llm.utils.get_provider import get_provider

from typing import Iterable, Union, Literal, Optional, Dict, List

import httpx
from openai import NotGiven, NOT_GIVEN
from openai._types import Headers, Query, Body
from openai.types.chat import ChatCompletionToolChoiceOptionParam, \
    ChatCompletionToolParam, \
    completion_create_params


def call_llm(
    messages: OpenAIMessages,
    model: ModelType,
    top_p: Optional[float] | NotGiven = None,
    temperature: Optional[float] | NotGiven = None,

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
    tool_choice: ChatCompletionToolChoiceOptionParam | NotGiven = None,
    tools: Iterable[ChatCompletionToolParam] | NotGiven = None,
    top_logprobs: Optional[int] | NotGiven = NOT_GIVEN,
    user: str | NotGiven = NOT_GIVEN,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = None, ):

    # logger.info(f">> calling LLM: Model={model}, Messages={messages}")

    res = get_provider(model).call(messages=messages,
        model=model,
        frequency_penalty=frequency_penalty,
        function_call=function_call,
        functions=functions,
        logit_bias=logit_bias,
        logprobs=logprobs,
        max_tokens=max_tokens,
        n=n,
        presence_penalty=presence_penalty,
        response_format=response_format,
        seed=seed,
        stop=stop,
        stream=stream,
        temperature=temperature,
        tool_choice=tool_choice,
        tools=tools,
        top_logprobs=top_logprobs,
        top_p=top_p,
        user=user,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout)
    logger.info(f"<< result: {res}")
    return res
