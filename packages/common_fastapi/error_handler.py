from functools import wraps
from typing import Callable

from fastapi import HTTPException
from loguru import logger


def error_handler(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # 尝试调用原始函数
            return await func(*args, **kwargs)
        except Exception as e:
            # 如果有异常，转换为HTTPException
            logger.error(e)
            raise HTTPException(status_code=400, detail=str(e))
    
    return wrapper
