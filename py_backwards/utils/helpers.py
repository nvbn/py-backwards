from inspect import getsource
import re
import sys
from typing import Any, Callable, Iterable, List, TypeVar
from functools import wraps
from ..conf import settings
from .. import messages

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


def get_source(fn: Callable[..., Any]) -> str:
    """Returns source code of the function."""
    source_lines = getsource(fn).split('\n')
    padding = len(re.findall(r'^(\s*)', source_lines[0])[0])
    return '\n'.join(line[padding:] for line in source_lines)


def warn(message: str) -> None:
    print(messages.warn(message), file=sys.stderr)


def debug(get_message: Callable[[], str]) -> None:
    if settings.debug:
        print(messages.debug(get_message()), file=sys.stderr)
