import asyncio

from loguru import logger

from src.llm_provider.utils import get_provider
from src.schema import ProviderType, ModelType
from src.utls.path import PROMPTS_PATH


async def conclude_wxmp_article(url: str):
    task = "conclude_wxmp_article"
    prompt_name = "conclude-wxmp-article.prompt.md"
    with open(PROMPTS_PATH.joinpath(prompt_name)) as f:
        prompt = f.read()
    messages = [
        {
            "role": "user",
            "content": prompt.format(url)
        }
    ]
    
    provider: ProviderType = "openai"
    model: ModelType = "gpt-3.5-turbo"
    logger.info(f">> calling LLM: Task={task}, Provider={provider}, Model={model}, Prompt={prompt_name}, Messages={messages}")
    res = get_provider(provider).call(
        model=model,
        messages=messages
    )
    logger.info(f"<< result: {res}")
    return res


if __name__ == '__main__':
    asyncio.run(conclude_wxmp_article("https://mp.weixin.qq.com/s?__biz=MzkwNzIyODk2OQ==&amp;amp;mid=2247490277&amp;amp;idx=1&amp;amp;sn=fcdf1d8aca24a9d4854683484a1ffe2c&amp;amp;chksm=c0dd38a3f7aab1b528fcdcfd51a98b9d036a78b62085656d76856e3b98acf2fdeef87f6535a5&amp;amp;mpshare=1&amp;amp;scene=1&amp;amp;srcid=0327ecXRJTqsBO7g6FD8KhaU&amp;amp;sharer_shareinfo=efb6657b14024743c11fee06a21dea25&amp;amp;sharer_shareinfo_first=39f2b0da0cbaaff768fd208187edcfc0#rd"))
