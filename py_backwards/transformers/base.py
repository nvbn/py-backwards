from abc import ABCMeta, abstractmethod
from typing import List
from typed_ast import ast3 as ast
from ..types import CompilationTarget, TransformationResult


class BaseTransformer(metaclass=ABCMeta):
    target = None  # type: CompilationTarget

    @classmethod
    @abstractmethod
    def transform(cls, tree: ast.AST) -> TransformationResult:
        ...


class BaseNodeTransformer(BaseTransformer, ast.NodeTransformer):
    dependencies = []  # type: List[str]

    def __init__(self, tree: ast.AST) -> None:
        super().__init__()
        self._tree = tree
        self._tree_changed = False

    @classmethod
    def transform(cls, tree: ast.AST) -> TransformationResult:
        inst = cls(tree)
        inst.visit(tree)
        return TransformationResult(tree, inst._tree_changed, cls.dependencies)
