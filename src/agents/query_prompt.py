from loguru import logger

from src.llm_provider.utils import get_provider
from src.schema import ProviderType, ModelType
from src.utls.path import AGENTS_PATH


def query_prompt(query: str, prompt_name: str, provider: ProviderType, model: ModelType):
    with open(AGENTS_PATH.joinpath(prompt_name)) as f:
        prompt = f.read()
    messages = [
        {
            "role": "system",
            "content": prompt,
        },
        {
            "role": "user",
            "content": query
        }
    ]
    
    logger.info(f">> calling LLM: Provider={provider}, Model={model}, Prompt.name={prompt_name}, Messages={messages}")
    res = get_provider(provider).call(
        model=model,
        messages=messages
    )
    logger.info(f"<< result: {res}")
    return res
