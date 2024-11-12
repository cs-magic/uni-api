from typing import Iterable, Union, Literal, Optional, Dict, List, TypeVar, Generic

import httpx
from openai import Client, NotGiven, NOT_GIVEN
from openai._types import Headers, Query, Body
from openai._utils import required_args
from openai.types.chat import ChatCompletionToolChoiceOptionParam, ChatCompletionToolParam, \
    completion_create_params

from packages.llm.schema import IMessage

M = TypeVar("M")


class LLMProviderBase(Generic[M]):
    name: str
    api_key: str | None
    base_url: str | None
    client: Client
    
    def __init__(self):
        super().__init__()
    
    @required_args(["messages", "model"], ["messages", "model", "stream"])
    def call(self,
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
             timeout: float | httpx.Timeout | None | NotGiven = None,
             ):
        # Convert messages to dict format if needed
        messages_dict = [
            {
                "role": msg["role"],
                "content": msg["content"]
            } for msg in messages
        ]
        
        return self.client.chat.completions.create(
            messages=messages_dict,
            model=model,
            top_p=top_p,
            timeout=timeout,
            # max_tokens=max_tokens, seed=seed, stop=stop, stream=stream, temperature=temperature, tool_choice=tool_choice, tools=tools,
        )
