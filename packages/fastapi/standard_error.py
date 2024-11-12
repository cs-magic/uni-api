from functools import wraps
from fastapi import HTTPException
from typing import Type, Union, Callable, Any
import traceback
import logging


def standard_error_handler(
    error_mapping: dict[Type[Exception], Union[int, tuple[int, str]]] = None
) -> Callable:
    """
    A decorator for standardizing error handling in FastAPI routes.

    Args:
        error_mapping: Optional dictionary mapping exception types to either:
            - status code (int)
            - tuple of (status_code, custom_message)

    Default behavior:
    - Catches all exceptions
    - Returns 500 for unknown errors
    - Maps common exceptions to appropriate status codes
    - Logs errors with traceback
    """

    default_error_mapping = {
        ValueError: 400,
        KeyError: 400,
        PermissionError: 403,
        NotImplementedError: 501,
    }

    if error_mapping:
        default_error_mapping.update(error_mapping)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)

            except HTTPException:
                # Re-raise FastAPI HTTP exceptions as-is
                raise

            except Exception as e:
                # Log the error with traceback
                logging.error(f"Error in {func.__name__}: {str(e)}")
                logging.debug(traceback.format_exc())

                # Find the most specific matching exception in the mapping
                for exc_type, mapping in default_error_mapping.items():
                    if isinstance(e, exc_type):
                        if isinstance(mapping, tuple):
                            status_code, message = mapping
                        else:
                            status_code = mapping
                            message = str(e)

                        raise HTTPException(
                            status_code=status_code,
                            detail=message
                        )

                # If no matching exception is found, return 500
                raise HTTPException(
                    status_code=500,
                    detail=f"Internal server error: {str(e)}"
                )

        return wrapper

    return decorator