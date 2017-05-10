from typed_ast import ast3 as ast
from ..const import TARGET_ALL
from .base import BaseNodeTransformer


class FormattedValuesTransformer(BaseNodeTransformer):
    """Compiles:
        f"hello {x}"
    To
        ''.join(['hello ', '{}'.format(x)])
    
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

        join_call = ast.Call(func=ast.Attribute(value=ast.Str(s=''),
                                                attr='join'),
                             args=[ast.List(elts=node.values)],
                             keywords=[])
        return self.generic_visit(join_call)  # type: ignore
