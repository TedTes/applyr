from __future__ import annotations

from collections.abc import Callable
from functools import wraps
import time
from typing import ParamSpec, TypeVar


P = ParamSpec("P")
T = TypeVar("T")


def retry(
    attempts: int = 3,
    delay_seconds: float = 0.1,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_error: BaseException | None = None
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_error = exc
                    if attempt == attempts:
                        break
                    time.sleep(delay_seconds)
            assert last_error is not None
            raise last_error

        return wrapper

    return decorator
