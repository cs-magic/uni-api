import time
from typing import Literal


def get_current_timestamp(kind: Literal["s", "ms", "ns"] = "s"):
    t = time.time_ns()
    if kind == "s":
        return t // 1e6
    if kind == "ms":
        return t // 1e3
    return t
