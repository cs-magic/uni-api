from src.llm_provider.moonshot import MoonshotProvider
from src.llm_provider.openai import OpenAIProvider
from src.schema import ProviderType


def get_provider(name: ProviderType):
    if name == "openai":
        return OpenAIProvider()
    
    elif name == "moonshot":
        return MoonshotProvider()
