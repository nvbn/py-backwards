
import sys
if sys.version_info >= (3, 8):
    import ast

    # A hack to allow astunparse to parse ast.Constant-s.
    import astunparse
    from types import SimpleNamespace as _SimpleNamespace

    def _Constant(self, tree):
        value = tree.value
        if isinstance(value, str):
            self._Str(_SimpleNamespace(s=value))
        elif isinstance(value, bytes):
            self._Bytes(_SimpleNamespace(s=value))
        elif value is Ellipsis:
            self._Ellipsis(tree)
        else:
            self._NameConstant(tree)

    def _NamedExpr(self, tree):
        self.write('(')
        self.dispatch(tree.target)
        self.write(' := ')
        self.dispatch(tree.value)
        self.write(')')


    if not hasattr(astunparse.Unparser, '_Constant'):
        astunparse.Unparser._Constant = _Constant
    if not hasattr(astunparse.Unparser, '_NamedExpr'):
        astunparse.Unparser._NamedExpr = _NamedExpr

    del _Constant, _NamedExpr
else:
    from typed_ast import ast3 as ast
