import sys
from ..utils.snippet import snippet
from ..utils.tree import insert_at
from .. import ast
from .base import BaseNodeTransformer

# "for arg in kwargs:" is a hack.
@snippet
def _sanity_check(func):
    for arg in _py_backwards_kwargs:
        raise TypeError(func + '() got an unexpected keyword argument ' +
            repr(arg))

class KwOnlyArgTransformer(BaseNodeTransformer):
    """Compiles:
        def test(a, b=1, *, c, d=2, **kwargs):
            pass

        test2 = lambda a, b=1, *, c=2, d=3 : d

        def test3(a, b=1, *, c, d=2):
            pass
    To
        def test(a, b=1, **kwargs):
            c = kwargs.pop('c')
            d = kwargs.pop('d', 2)
            pass

        test2 = lambda a, b=1, c=2, d=3 : d

        def test3(a, b=1, **_py_backwards_kwargs):
            c = _py_backwards_kwargs.pop('c')
            d = _py_backwards_kwargs.pop('d', 2)
            for arg in _py_backwards_kwargs:
                raise TypeError('test3() got an unexpected keyword argument '
                                + repr(arg))

    """
    target = (2, 7)

    def visit_FunctionDef(self, node: ast.FunctionDef) \
            -> ast.FunctionDef:
        if node.args.kwonlyargs:
            self._tree_changed = True
            docstring = None
            if isinstance(node.body[0], ast.Expr) and \
                    isinstance(node.body[0].value, ast.Str):
                docstring = node.body.pop(0)

            if node.args.kwarg:
                kwarg = ast.Name(id=node.args.kwarg.arg, ctx=ast.Load())
            else:
                kwarg = ast.Name(id='_py_backwards_kwargs', ctx=ast.Load())
                node.args.kwarg = ast.arg(arg='_py_backwards_kwargs',
                                          annotation=None)
                insert_at(0, node,
                          _sanity_check.get_body(func=ast.Str(s=node.name)))

            for i, arg in enumerate(node.args.kwonlyargs):
                args = [ast.Str(arg.arg)] # type: list
                if node.args.kw_defaults[i]:
                    args.append(node.args.kw_defaults[i])
                insert_at(i, node, ast.Assign(targets=[ast.Name(id=arg.arg)],
                    value=ast.Call(func=ast.Attribute(value=kwarg,
                    attr='pop'), args=args, keywords=[])))

            node.args.kwonlyargs.clear()
            node.args.kw_defaults.clear()

            if docstring:
                node.body.insert(0, docstring)

        return self.generic_visit(node)  # type: ignore

    # Just make all paramters positional in lambdas
    def visit_Lambda(self, node: ast.Lambda) -> ast.Lambda:
        if not node.args.vararg and node.args.kwonlyargs:
            self._tree_changed = True
            node.args.args.extend(node.args.kwonlyargs)
            node.args.kwonlyargs.clear()
            node.args.defaults.extend(node.args.kw_defaults)
            node.args.kw_defaults.clear()

        return self.generic_visit(node)  # type: ignore
