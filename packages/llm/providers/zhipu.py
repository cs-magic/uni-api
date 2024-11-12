from zhipuai import ZhipuAI

from settings import settings
from packages.llm.providers._base import LLMProviderBase
from packages.llm.schema import ZhipuModel


class ZhipuProvider(LLMProviderBase[ZhipuModel]):
    name = "zhipu"
    base_url = None
    api_key = settings.ZHIPU_API_KEY
    client = ZhipuAI(api_key=api_key, base_url=base_url)
