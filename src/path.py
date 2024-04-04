import pathlib

PATH_PATH = pathlib.Path(__file__)
SRC_PATH = PATH_PATH.parent
PROJECT_PATH = SRC_PATH.parent
AGENTS_PATH = SRC_PATH.joinpath("agents")
