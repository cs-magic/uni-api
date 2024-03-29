from unittest import TestCase, IsolatedAsyncioTestCase

from src.router.agent import call_agent
from src.utls.path import AGENTS_PATH


class Test(IsolatedAsyncioTestCase):
    async def test_call_agent(self):
        with open(AGENTS_PATH.joinpath("conclude-article.sample.md")) as f:
            content = f.read()
        await call_agent(content, "conclude-article", "moonshot-v1-8k")
