import pathlib

PATH_PATH = pathlib.Path(__file__)
PROJECT_PATH = PATH_PATH.parent
GENERATED_PATH = PROJECT_PATH.joinpath(".generated")
GENERATED_PATH.mkdir(exist_ok=True)
