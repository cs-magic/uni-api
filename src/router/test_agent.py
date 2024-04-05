from unittest import IsolatedAsyncioTestCase

from src.router.agent import call_agent_route
from src.path import AGENT_CONFIG_PATH


class Test(IsolatedAsyncioTestCase):
    async def test_call_agent(self):
        # logger.remove()
        with open(AGENT_CONFIG_PATH.joinpath("article-summariser.sample.md")) as f:
            content = f.read()
        await call_agent_route(content, "article-summariser",
            # "gpt-3.5-turbo",
            "gpt-4"
            # "moonshot-v1-8k"
            # 'glm-4',
            # "abab6-chat"
        )
