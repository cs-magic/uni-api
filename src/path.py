import pathlib

PATH_PATH = pathlib.Path(__file__)
SRC_PATH = PATH_PATH.parent
PROJECT_PATH = SRC_PATH.parent
AGENT_PATH = SRC_PATH.joinpath("agent")
AGENT_CONFIG_PATH = AGENT_PATH.joinpath("config")
