import pathlib

import yaml

from packages.common_common.compress_content import compress_content
from packages.common_llm.agent.call_llm import call_llm
from packages.common_llm.agent.schema import AgentType, AgentConfig
from packages.common_llm.schema import ModelType


def call_agent(input: str, agent_type: AgentType, llm_model_type: ModelType):
    config_dir = pathlib.Path(__file__).parent.joinpath("config")
    with open(config_dir.joinpath(f"{agent_type}.agent.yml")) as f:
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
    
    return call_llm(
        messages,
        model,
        max_tokens=agent.total_tokens,
        # todo: more args
    )


if __name__ == '__main__':
    # call_agent("hello", "default", "gpt-3.5-turbo")
    call_agent("hello", "default", "qwen-turbo")
