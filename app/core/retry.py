import asyncio
import logging
from typing import Callable, TypeVar, Awaitable, Union

logger = logging.getLogger(__name__)

T = TypeVar("T")

async def with_retries(
    coro_factory: Callable[[], Awaitable[T]],
    retries: int = 2,
    delay: float = 0.5,
    backoff: float = 2.0
) -> T:
    """
    Executes an async function with retries.
    
    Args:
        coro_factory: A function that returns the coroutine to await. 
                      Must be a factory to create a fresh coroutine on each try.
        retries: Number of retries allowed (total attempts = retries + 1).
        delay: Initial delay between retries in seconds.
        backoff: Multiplier for delay after each failure.
    """
    last_exc: Exception | None = None
    
    for i in range(retries + 1):
        try:
            return await coro_factory()
        except Exception as e:
            last_exc = e
            if i < retries:
                wait_time = delay * (backoff ** i)
                logger.warning(f"Attempt {i+1} failed: {e}. Retrying in {wait_time:.2f}s...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"All {retries + 1} attempts failed. Last error: {e}")
                
    if last_exc:
        raise last_exc
    raise RuntimeError("Unexpected retry loop exit")
