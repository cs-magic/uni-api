import time

from loguru import logger


class Tracker:
    
    def __init__(self):
        self._t = time.time()
    
    def track(self, name: str = None, update=False):
        t = time.time()
        logger.info(f"[{t - self._t:.2f}s] {name}")
        if update:
            self._t = t
