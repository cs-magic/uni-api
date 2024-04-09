import re

from loguru import logger


def parse_first_url(input: str):
    m = re.search(r"https?://[^\s，。]+|www\.[^\s，。]+", input)
    output = m[0] if m else None
    logger.debug(f"-- parsed first url: (Input={input}, Output={output})", )
    return output
