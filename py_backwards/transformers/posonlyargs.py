import sys
from ..const import TARGET_ALL
from ..utils.helpers import VariablesGenerator
from ..utils.tree import insert_at
from .. import ast
from .base import BaseNodeTransformer

# Caution: Since this is a Python 3.8+ transformer, posonlyargs won't exist on
#   Python 3.7 and below, and astunparse can't unparse positional-only
#   arguments.
PY38 = sys.version_info >= (3, 8)

class PosOnlyArgTransformer(BaseNodeTransformer):
    """Compiles:
        def test(a, /, b, *, c):
            pass

        def test2(a, /, b, *, c, **kwargs):
            pass
    To
        def test(a, b, *, c):
            pass

        def test2(<mangled name>, b, *, c, **kwargs):
            a = <mangled name>
            del <mangled name>

    """
    target = TARGET_ALL

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        if PY38 and getattr(node.args, 'posonlyargs', None):
            self._tree_changed = True
            args = node.args.posonlyargs # type: ignore
            if node.args.kwarg:
                docstring = None
                if isinstance(node.body[0], ast.Expr) and \
                        isinstance(node.body[0].value, ast.Str):
                    docstring = node.body.pop(0)

                # Generate mangled names with VariablesGenerator to ensure they
                #   don't conflict with anything.
                for i, arg in enumerate(args):
                    name = arg.arg
                    arg.arg = VariablesGenerator.generate('\u036f' + name)
                    insert_at(i, node, ast.Assign(targets=[ast.Name(id=name)],
                        value=ast.Name(id=arg.arg, ctx=ast.Load())))

                del_node = ast.Delete(targets=[ast.Name(id=arg.arg,
                                                        ctx=ast.Del())
                                               for arg in args])
                insert_at(i + 1, node, del_node)

                if docstring:
                    node.body.insert(0, docstring)

            args.extend(node.args.args)
            node.args.args = args
            node.args.posonlyargs = [] # type: ignore

        return self.generic_visit(node)  # type: ignore

    def visit_Lambda(self, node: ast.Lambda) -> ast.Lambda:
        if PY38 and getattr(node.args, 'posonlyargs', None):
            self._tree_changed = True
            args = node.args.posonlyargs # type: ignore
            args.extend(node.args.args)
            node.args.args = args
            node.args.posonlyargs = [] # type: ignore

        return self.generic_visit(node)  # type: ignore
