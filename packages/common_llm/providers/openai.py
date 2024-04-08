from openai import Client

from settings import settings
from packages.common_llm.providers._base import LLMProviderBase
from packages.common_llm.schema import OpenAIModel


class OpenAIProvider(LLMProviderBase[OpenAIModel]):
    name = "openai"
    base_url = None
    api_key = settings.OPENAI_API_KEY
    client = Client(api_key=api_key, base_url=base_url)
