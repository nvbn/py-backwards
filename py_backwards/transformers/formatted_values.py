from typed_ast import ast3 as ast
from .base import BaseTransformer


class FormattedValuesTransformer(BaseTransformer):
    target = (3, 5)

    def visit_FormattedValue(self, node):
        if node.format_spec:
            template = ''.join(['{:', node.format_spec.s, '}'])
        else:
            template = '{}'

        format_call = ast.Call(func=ast.Attribute(value=ast.Str(s=template),
                                                  attr='format'),
                               args=[node.value],
                               keywords=[])
        return self.generic_visit(format_call)

    def visit_JoinedStr(self, node):
        join_call = ast.Call(func=ast.Attribute(value=ast.Str(s=''),
                                                attr='join'),
                             args=[ast.List(elts=node.values)],
                             keywords=[])
        return self.generic_visit(join_call)