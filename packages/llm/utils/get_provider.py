from packages.llm.providers.ali import DashscopeProvider
from packages.llm.providers.anthropic import AnthropicProvider
from packages.llm.providers.minimax import MinimaxProvider
from packages.llm.providers.moonshot import MoonshotProvider
from packages.llm.providers.openai import OpenAIProvider
from packages.llm.providers.zhipu import ZhipuProvider
from packages.llm.schema import ModelType, BaichuanModel


def get_provider(model: ModelType):
    if model.startswith("gpt"):
        return OpenAIProvider()

    elif model.startswith("moonshot"):
        return MoonshotProvider()

    elif model.startswith("glm"):
        return ZhipuProvider()

    elif model.startswith("abab"):
        return MinimaxProvider()

    elif model.startswith("qwen"):
        return DashscopeProvider()

    elif model.startswith("claude"):
        return AnthropicProvider()

    elif model.startswith("Baichuan"):
        return BaichuanModel()

    raise Exception(f"no provider from model(name={model})")
