import os

import dotenv

# dotenv.load_dotenv()

for k, v in os.environ.items():
    if "wechaty" in k.lower():
        print(k, "-->", v)
