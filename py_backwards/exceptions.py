from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from .transformers.base import BaseTransformer


class CompilationError(Exception):
    """Raises when compilation failed because fo syntax error."""

    def __init__(self, filename: str, code: str,
                 lineno: int, offset: int) -> None:
        self.filename = filename
        self.code = code
        self.lineno = lineno
        self.offset = offset


class TransformationError(Exception):
    """Raises when transformation failed."""

    def __init__(self, filename: str,
                 transformer: 'Type[BaseTransformer]',
                 ast: str,
                 traceback: str) -> None:
        self.filename = filename
        self.transformer = transformer
        self.ast = ast
        self.traceback = traceback


class InvalidInputOutput(Exception):
    """Raises when input is a directory, but output is a file."""


class InputDoesntExists(Exception):
    """Raises when input doesn't exists."""


class NodeNotFound(Exception):
    """Raises when node not found."""
