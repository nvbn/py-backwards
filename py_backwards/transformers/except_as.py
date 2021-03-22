from .. import ast, unparse
from .base import BaseNodeTransformer

class ExceptAsTransformer(BaseNodeTransformer):
    """Compiles:
        try:
            1 / 0
        except ZeroDivisionError as e:
            print(repr(e))
    To
        try:
            1 / 0
        except ZeroDivisionError, e:
            print(repr(e))

    """
    target = (2, 5)

    def visit_Try(self, node: ast.Try) -> ast.Try:
        # This is a hack.
        for handler in node.handlers:
            if handler.type and handler.name:
                self._tree_changed = True
                name = unparse(handler.type).strip() + ', ' + handler.name
                handler.type = ast.Name(id=name)
                handler.name = None

        return self.generic_visit(node)  # type: ignore
