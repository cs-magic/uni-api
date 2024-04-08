from openai import Client

from settings import settings
from packages.common_llm.providers._base import LLMProviderBase
from packages.common_llm.schema import MoonshotModel


class MoonshotProvider(LLMProviderBase[MoonshotModel]):
    name = "moonshot"
    base_url = "https://api.moonshot.cn/v1"
    api_key = settings.MOONSHOT_API_KEY
    client = Client(api_key=api_key, base_url=base_url)
