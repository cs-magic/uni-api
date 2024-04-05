import time

from loguru import logger


class Tracker:
    
    def __init__(self):
        self.t = time.time()
    
    def track(self, name: str = None):
        t = time.time()
        logger.info(f"[{t - self.t:.2f}s] {name}, t={t}")
        self.t = t
