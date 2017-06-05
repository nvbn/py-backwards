import functools

from typed_ast import ast3 as ast
from ..const import TARGET_ALL
from .base import BaseNodeTransformer


class FormattedValuesTransformer(BaseNodeTransformer):
    """Compiles:
        f"hello {x}"
    To
        'hello ' + '{}'.format(x)
    
    """
    target = TARGET_ALL

    def visit_FormattedValue(self, node: ast.FormattedValue) -> ast.Call:
        self._tree_changed = True

        if node.format_spec:
            template = ''.join(['{:', node.format_spec.s, '}'])  # type: ignore
        else:
            template = '{}'

        format_call = ast.Call(func=ast.Attribute(value=ast.Str(s=template),
                                                  attr='format'),
                               args=[node.value],
                               keywords=[])
        return self.generic_visit(format_call)  # type: ignore

    def visit_JoinedStr(self, node: ast.JoinedStr) -> ast.Call:
        self._tree_changed = True
        NONE = ast.Str(s='')

        init = ast.BinOp(left=NONE, right=NONE, op=ast.Add())

        def to_binop(acc, next):
            left, right, op = acc.left, acc.right, acc.op
            if left is NONE:
                return ast.BinOp(left=right, right=next, op=op)
            return ast.BinOp(left=acc, right=next, op=op)

        value = functools.reduce(to_binop, node.values, init)
        concat_expr = ast.Expr(value=value)

        return self.generic_visit(concat_expr)  # type: ignore
