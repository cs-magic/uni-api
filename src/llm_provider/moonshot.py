from settings import settings
from src.llm_provider.base import LLMProviderBase
from src.schema import MoonshotModel


class MoonshotProvider(LLMProviderBase[MoonshotModel]):
    name = "moonshot"
    
    base_url = "https://api.moonshot.cn/v1"
    api_key = settings.MOONSHOT_API_KEY
