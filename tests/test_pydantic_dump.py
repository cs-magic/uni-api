import json

from packages.spider.schema import ISummary
from v1_plain.src import GENERATED_PATH

if __name__ == '__main__':
    model = ISummary(modelType="gpt-3.5-turbo", result="你好啊 hello")
    with open(GENERATED_PATH.joinpath("test-pydantic-dump.json"), "w") as f:
        json.dump(model.dict(), f, ensure_ascii=False)
        # json.dump(model.json(), f)
