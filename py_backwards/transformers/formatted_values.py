from typed_ast import ast3 as ast
from .base import BaseTransformer


class FormattedValuesTransformer(BaseTransformer):
    """Compiles:
        f"hello {x}"
    To
        ''.join(['hello ', '{}'.format(x)])
    
    """
    target = (3, 5)

    def visit_FormattedValue(self, node: ast.FormattedValue) -> ast.Call:
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
        join_call = ast.Call(func=ast.Attribute(value=ast.Str(s=''),
                                                attr='join'),
                             args=[ast.List(elts=node.values)],
                             keywords=[])
        return self.generic_visit(join_call)  # type: ignore
