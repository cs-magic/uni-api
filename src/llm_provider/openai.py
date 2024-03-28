from settings import settings
from src.llm_provider.base import LLMProviderBase
from src.schema import OpenAIModel


class OpenAIProvider(LLMProviderBase[OpenAIModel]):
    name = "openai"
    
    base_url = None
    api_key = settings.OPENAI_API_KEY
