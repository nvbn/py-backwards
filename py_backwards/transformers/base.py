from typed_ast import ast3 as ast
from ..types import CompilationTarget


class BaseTransformer(ast.NodeTransformer):
    target = None  # type: CompilationTarget

    @classmethod
    def transform(cls, tree: ast.AST) -> ast.AST:
        inst = cls()
        inst.visit(tree)
        return tree
