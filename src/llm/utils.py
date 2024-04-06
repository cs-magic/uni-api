from src.llm.providers.minimax import MinimaxProvider
from src.llm.providers.moonshot import MoonshotProvider
from src.llm.providers.openai import OpenAIProvider
from src.llm.providers.zhipu import ZhipuProvider
from src.schema.llm import ModelType


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
