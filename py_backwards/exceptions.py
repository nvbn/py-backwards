from typing import Type
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

    def __init__(self, filename: str, transformer: Type[BaseTransformer],
                 traceback: str) -> None:
        self.filename = filename
        self.transformer = transformer
        self.traceback = traceback
