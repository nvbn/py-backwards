from typing import Any, Callable, Iterable, List, TypeVar
from functools import wraps

T = TypeVar('T')


def eager(fn: Callable[..., Iterable[T]]) -> Callable[..., List[T]]:
    @wraps(fn)
    def wrapped(*args: Any, **kwargs: Any) -> List[T]:
        return list(fn(*args, **kwargs))

    return wrapped
