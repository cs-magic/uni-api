from typing import Iterable, Union, Literal, Optional, Dict, List

import httpx
import requests
from openai import NotGiven, NOT_GIVEN
from openai._types import Headers, Query, Body
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolChoiceOptionParam, ChatCompletionToolParam, \
    completion_create_params

from settings import settings
from src.llm.providers._base import LLMProviderBase
from src.schema import OpenAIModel, MinimaxModel


class MinimaxProvider(LLMProviderBase[OpenAIModel]):
    name = "minimax"
    
    base_url = None
    api_key = settings.MINIMAX_API_KEY
    group_id = settings.MINIMAX_GROUP_ID
    
    def call(self,
             *,
             messages: List[ChatCompletionMessageParam],
             model: MinimaxModel,
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
        url = "https://api.minimax.chat/v1/text/chatcompletion_pro?GroupId=" + self.group_id
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + self.api_key}
        
        system_message = messages[0]
        payload = {
            "bot_setting": [
                {
                    "bot_name": "system",
                    "content": "MM智能助理是一款由MiniMax自研的，没有调用其他产品的接口的大型语言模型。MiniMax是一家中国科技公司，一直致力于进行大模型相关的研究。"
                    if not system_message or system_message["role"] != "system" else system_message['content'],
                }
            ],
            # todo:  {"created":0,"model":"abab6-chat","reply":"","choices":null,"base_resp":{"status_code":2013,"status_msg":"invalid params, messages中sender_name、sender_type不能为空"}}
            "messages":
                [{"send_type": "USER", "send_name": "小明", "text": message["content"]} for message in messages if
                 message["role"] == "user"],
            "reply_constraints": {"sender_type": "BOT", "sender_name": "system"},
            "model": "abab6-chat",
            "tokens_to_generate": 1034,
            "temperature": 0.01,
            "top_p": 0.95,
        }
        print(payload)
        
        response = requests.request("POST", url, headers=headers, json=payload)
        return {
            "choices": [
                {
                    "message": {
                        "content": response.text
                    }
                }
            ]
        }
