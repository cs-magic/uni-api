from zhipuai import ZhipuAI

from settings import settings
from src.llm.providers._base import LLMProviderBase
from src.schema.llm import ZhipuModel


class ZhipuProvider(LLMProviderBase[ZhipuModel]):
    name = "zhipu"
    base_url = None
    api_key = settings.ZHIPU_API_KEY
    client = ZhipuAI(api_key=api_key, base_url=base_url)
