from src.llm_provider.moonshot import MoonshotProvider
from src.llm_provider.openai import OpenAIProvider
from src.schema import ProviderType


def get_provider(model: str):
    if model.startswith("gpt"):
        return OpenAIProvider()
    
    elif model.startswith("moonshot"):
        return MoonshotProvider()
    
    raise Exception(f"no provider from model(name={model})")
