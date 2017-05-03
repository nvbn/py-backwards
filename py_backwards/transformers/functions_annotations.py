from typed_ast import ast3 as ast
from .base import BaseNodeTransformer


class FunctionsAnnotationsTransformer(BaseNodeTransformer):
    """Compiles:
        def fn(x: int) -> int:
            pass
    To:
        def fn(x):
            pass
            
    """
    target = (2, 7)

    def visit_arg(self, node: ast.arg) -> ast.arg:
        self._tree_changed = True
        node.annotation = None
        return self.generic_visit(node)  # type: ignore

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._tree_changed = True
        node.returns = None
        return self.generic_visit(node)  # type: ignore
