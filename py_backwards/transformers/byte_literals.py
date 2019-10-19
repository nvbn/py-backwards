from .. import ast
from .base import BaseNodeTransformer

# Python2-style unicode and str repr()s, astunparse should call these
#   overridden functions.
class _py2_unicode(str):
    __slots__ = ()
    def __repr__(self):
        return 'u' + super().__repr__()

class _py2_str(bytes):
    __slots__ = ()
    def __repr__(self):
        return super().__repr__().lstrip('b')

class ByteLiteralTransformer(BaseNodeTransformer):
    """Compiles:
        test = 'Hello, world!'
        test2 = b'test'
    To
        test = u'Hello, world!'
        test2 = 'test'

    """
    target = (2, 5)

    def visit_Str(self, node: ast.Str) -> ast.Str:
        self._tree_changed = True
        node.s = _py2_unicode(node.s)
        return self.generic_visit(node)  # type: ignore

    def visit_Bytes(self, node: ast.Bytes) -> ast.Bytes:
        self._tree_changed = True
        node.s = _py2_str(node.s)
        return self.generic_visit(node)  # type: ignore
