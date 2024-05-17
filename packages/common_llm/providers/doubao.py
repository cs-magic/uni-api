from volcenginesdkarkruntime import Ark

from packages.common_llm.providers._base import LLMProviderBase
from packages.common_llm.schema import DoubaoModel
from settings import settings


class DoubaoProvider(LLMProviderBase[DoubaoModel]):
    name = "doubao"
    api_key = settings.DOUBAO_API_KEY
    client = Ark(api_key=api_key)
