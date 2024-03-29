import pathlib

PATH_PATH = pathlib.Path(__file__)
UTILS_PATH = PATH_PATH.parent
SRC_PATH = UTILS_PATH.parent
PROJECT_PATH = SRC_PATH.parent
AGENTS_PATH = SRC_PATH.joinpath("agents")
