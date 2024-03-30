from openai import Client

from settings import settings
from src.llm.providers._base import LLMProviderBase
from src.schema import OpenAIModel


class OpenAIProvider(LLMProviderBase[OpenAIModel]):
    name = "openai"
    
    base_url = None
    api_key = settings.OPENAI_API_KEY

    client = Client(api_key=api_key, base_url=base_url)
