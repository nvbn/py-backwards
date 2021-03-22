from .. import ast
from .base import BaseNodeTransformer

class RaiseFromTransformer(BaseNodeTransformer):
    """Compiles:
        raise TypeError('Bad') from exc
    To
        raise TypeError('Bad')

    """
    target = (2, 7)

    def visit_Raise(self, node: ast.Raise) -> ast.Raise:
        if node.cause:
            self._tree_changed = True
            node.cause = None

        return self.generic_visit(node)  # type: ignore
