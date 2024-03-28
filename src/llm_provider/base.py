import os
from typing import Iterable, Union, Literal, Optional, Dict, List

import httpx
from openai import Client, NotGiven, NOT_GIVEN
from openai._types import Headers, Query, Body
from openai._utils import required_args
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolChoiceOptionParam, ChatCompletionToolParam, \
    completion_create_params


class LLMProvider:
    name: str
    
    client: Client
    
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        
        if name == "moonshot":
            base_url = "https://api.moonshot.cn/v1"
            api_key = os.environ["MOONSHOT_API_KEY"]
        else:
            base_url = None
            api_key = None
        
        self.client = Client(api_key=api_key, base_url=base_url)
    
    @required_args(["messages", "model"], ["messages", "model", "stream"])
    def call(self,
             *,
             messages: Iterable[ChatCompletionMessageParam],
             model: str,
             frequency_penalty: Optional[float] | NotGiven = NOT_GIVEN,
             function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
             functions: Iterable[completion_create_params.Function] | NotGiven = NOT_GIVEN,
             logit_bias: Optional[Dict[str, int]] | NotGiven = NOT_GIVEN,
             logprobs: Optional[bool] | NotGiven = NOT_GIVEN,
             max_tokens: Optional[int] | NotGiven = NOT_GIVEN,
             n: Optional[int] | NotGiven = NOT_GIVEN,
             presence_penalty: Optional[float] | NotGiven = NOT_GIVEN,
             response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN,
             seed: Optional[int] | NotGiven = NOT_GIVEN,
             stop: Union[Optional[str], List[str]] | NotGiven = NOT_GIVEN,
             stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
             temperature: Optional[float] | NotGiven = NOT_GIVEN,
             tool_choice: ChatCompletionToolChoiceOptionParam | NotGiven = NOT_GIVEN,
             tools: Iterable[ChatCompletionToolParam] | NotGiven = NOT_GIVEN,
             top_logprobs: Optional[int] | NotGiven = NOT_GIVEN,
             top_p: Optional[float] | NotGiven = NOT_GIVEN,
             user: str | NotGiven = NOT_GIVEN,
             # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
             # The extra values given here take precedence over values defined on the client or passed to this method.
             extra_headers: Headers | None = None,
             extra_query: Query | None = None,
             extra_body: Body | None = None,
             timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
             ):
        
        return self.client.chat.completions.create(messages=messages, model=model, frequency_penalty=frequency_penalty, function_call=function_call, functions=functions, logit_bias=logit_bias, logprobs=logprobs, max_tokens=max_tokens, n=n, presence_penalty=presence_penalty, response_format=response_format, seed=seed, stop=stop, stream=stream, temperature=temperature, tool_choice=tool_choice, tools=tools, top_logprobs=top_logprobs, top_p=top_p, user=user, extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout)
