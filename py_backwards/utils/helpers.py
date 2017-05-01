from typing import Any, Callable, Iterable, List, TypeVar
from functools import wraps

T = TypeVar('T')


def eager(fn: Callable[..., Iterable[T]]) -> Callable[..., List[T]]:
    @wraps(fn)
    def wrapped(*args: Any, **kwargs: Any) -> List[T]:
        return list(fn(*args, **kwargs))

    return wrapped


class VariablesGenerator:
    _counter = 0

    @classmethod
    def generate(cls, variable: str) -> str:
        """Generates unique name for variable."""
        try:
            return '_py_backwards_{}_{}'.format(variable, cls._counter)
        finally:
            cls._counter += 1
