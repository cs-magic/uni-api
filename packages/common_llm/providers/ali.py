from http import HTTPStatus
from typing import Iterable, Union, Literal, Optional, Dict, List

import dashscope
import httpx
from openai import NotGiven, NOT_GIVEN
from openai._types import Headers, Query, Body
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolChoiceOptionParam, ChatCompletionToolParam, \
    completion_create_params

from packages.common_llm.providers._base import LLMProviderBase
from packages.common_llm.schema import DashscopeModel
from settings import settings


class DashscopeProvider(LLMProviderBase[DashscopeModel]):
    name = "dashscope"
    base_url = None
    api_key = settings.DASHSCOPE_API_KEY
    
    def call(self,
             *,
             messages: List[ChatCompletionMessageParam],
             model: DashscopeModel,
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
        
        response = dashscope.Generation.call(
            model,
            messages=messages,
            result_format='message',  # set the result to be "message" format.
        )
        if response.status_code == HTTPStatus.OK:
            print(response)
            return response.output
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))
            raise Exception(response.message)
