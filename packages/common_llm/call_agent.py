import yaml
from loguru import logger

from packages.common_algo.string import compress_content
from packages.common_llm.agent.schema import AgentType, AgentConfig
from packages.common_llm.utils import get_provider
from src.path import AGENT_CONFIG_PATH
from packages.common_llm.schema import ModelType


def call_agent(input: str, agent_type: AgentType, llm_model_type: ModelType):
    with open(AGENT_CONFIG_PATH.joinpath(f"{agent_type}.agent.yml")) as f:
        agent = AgentConfig.parse_obj(yaml.safe_load(f))
    
    model = llm_model_type if llm_model_type else agent.model
    
    system_prompt = agent.system_prompt or ""
    messages = []
    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt,
        })
    
    max_content_len = (
        agent.total_tokens
        - len(system_prompt)  # 系统prompt的长度
        - 1e3  # 输出的预留长度
        - 1e2  # 误差
    )
    content = compress_content(input, max_content_len)
    
    messages.append({
        "role": "user",
        "content": content
    })
    
    logger.info(f">> calling LLM: Agent={agent}, Messages={messages}")
    res = get_provider(model).call(
        model=model,
        messages=messages,
        top_p=0.03,  # ref: https://platform.openai.com/docs/api-reference/chat/create
        # temperature=0
    )
    logger.info(f"<< result: {res}")
    return res.choices[0].message.content


if __name__ == '__main__':
    call_agent("hello", "default", "gpt-3.5-turbo")
