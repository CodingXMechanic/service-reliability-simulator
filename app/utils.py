# app/utils.py
import asyncio
import random
from typing import Callable, Coroutine, Any
from .logger import logger


async def process_value(value: float) -> dict:
    """
    Simple, deterministic processing for demonstration:
    - Double the input and return result with an explanation.
    Keep this tiny so it's easy to explain in interviews.
    """
    # Example "computation"
    result = value * 2
    logger.info("processed value", extra={"endpoint": "/process", "message": f"input={value}", "result": result})
    return {"input": value, "result": result}


async def retry_async(action: Callable[[], Coroutine[Any, Any, Any]],
                      max_retries: int = 2,
                      backoff_seconds: float = 0.2) -> Any:
    """
    Retry wrapper for async operations.
    - Retries on Exception.
    - Simple, interview-friendly exponential-ish backoff.
    - Logs each attempt so it's easy to show retry behavior in logs.
    """
    last_exc = None
    for attempt in range(1, max_retries + 2):  # e.g. max_retries=2 -> attempts 1..3
        try:
            logger.info("retry attempt", extra={"endpoint": "retry_async", "message": f"attempt={attempt}"})
            return await action()
        except Exception as exc:
            last_exc = exc
            logger.warning("retry failure",
                           extra={"endpoint": "retry_async", "error_reason": str(exc), "message": f"attempt={attempt}"})
            if attempt <= max_retries:
                await asyncio.sleep(backoff_seconds * attempt)
            else:
                logger.error("max retries reached", extra={"endpoint": "retry_async", "error_reason": str(exc)})
                raise