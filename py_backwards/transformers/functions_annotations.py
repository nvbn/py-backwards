from typed_ast import ast3 as ast
from typed_astunparse import unparse
from .base import BaseNodeTransformer


class FunctionsAnnotationsTransformer(BaseNodeTransformer):
    """Compiles:
        def fn(x: int) -> int:
            pass
    To:
        def fn(x):
            # type: (int) -> int
            pass
            
    """
    target = (2, 7)

    def visit_arg(self, node: ast.arg) -> ast.arg:
        self._tree_changed = True
        node._annotation = node.annotation
        node.annotation = None
        return self.generic_visit(node)  # type: ignore

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._tree_changed = True

        returns = node.returns
        node.returns = None

        node = self.generic_visit(node)  # type: ignore

        args_types = [unparse(arg._annotation).strip() for arg in node.args.args if arg._annotation is not None]
        if getattr(node.args.vararg, '_annotation', None) is not None:
            args_types += ['*' + unparse(node.args.vararg._annotation).strip()]
        args_types += [unparse(arg._annotation).strip() for arg in node.args.kwonlyargs if arg._annotation is not None]
        if getattr(node.args.kwarg, '_annotation', None) is not None:
            args_types += ['**' + unparse(node.args.kwarg._annotation).strip()]

        if returns:
            node.type_comment = '(' + (', '.join(args_types)) + ') -> ' + unparse(returns).strip()

        return node
