from packages.common_llm.providers.minimax import MinimaxProvider
from packages.common_llm.providers.moonshot import MoonshotProvider
from packages.common_llm.providers.openai import OpenAIProvider
from packages.common_llm.providers.zhipu import ZhipuProvider
from packages.common_llm.schema import ModelType


def get_provider(model: ModelType):
    if model.startswith("gpt"):
        return OpenAIProvider()
    
    elif model.startswith("moonshot"):
        return MoonshotProvider()
    
    elif model.startswith("glm"):
        return ZhipuProvider()
    
    elif model.startswith("abab"):
        return MinimaxProvider()
    
    raise Exception(f"no provider from model(name={model})")
