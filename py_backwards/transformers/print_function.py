from ..utils.snippet import snippet
from ..utils.tree import insert_at
from .. import ast
from .base import BaseNodeTransformer

@snippet
def _import():
    from six import print_ as _py_backwards_print

class PrintFunctionTransformer(BaseNodeTransformer):
    """Compiles:
        print('Hello world', end='!\n')
    To
        _py_backwards_print('Hello world', end='!\n')

    """
    target = (2, 5)
    dependencies = ['six']

    def visit_Module(self, node: ast.Module) -> ast.Module:
        insert_at(0, node, _import.get_body())
        return self.generic_visit(node)  # type: ignore

    def visit_Name(self, node: ast.Name) -> ast.Name:
        if node.id == 'print':
            self._tree_changed = True
            node.id = '_py_backwards_print'

        return self.generic_visit(node)  # type: ignore
