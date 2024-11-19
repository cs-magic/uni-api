import pathlib

PATH_PATH = pathlib.Path(__file__)
UTILS_PATH = PATH_PATH.parent
PROJECT_PATH = UTILS_PATH.parent
DATA_PATH = PROJECT_PATH / "data"
GENERATED_PATH = PROJECT_PATH.joinpath(".generated")
GENERATED_PATH.mkdir(exist_ok=True)
