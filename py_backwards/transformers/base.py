from abc import ABCMeta, abstractmethod
from typed_ast import ast3 as ast
from ..types import CompilationTarget


class BaseTransformer(metaclass=ABCMeta):
    target = None  # type: CompilationTarget

    @classmethod
    @abstractmethod
    def transform(cls, tree: ast.AST) -> ast.AST:
        ...


class BaseNodeTransformer(BaseTransformer, ast.NodeTransformer):
    @classmethod
    def transform(cls, tree: ast.AST) -> ast.AST:
        inst = cls()
        inst.visit(tree)
        return tree
