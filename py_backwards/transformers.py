from typed_ast import ast3 as ast
from astunparse import unparse


class FormattedValuesTransformer(ast.NodeTransformer):
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
                             args=[ast.List(elts=node.values, ctx=ast.Load())],
                             keywords=[])
        return self.generic_visit(join_call)


class AnnotationsTransformer(ast.NodeTransformer):
    def visit_arg(self, node):
        node.annotation = None
        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        node.returns = None
        return self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if node.value is None:
            return

        return self.generic_visit(ast.Assign(targets=[node.target],
                                             value=node.value))


transformers = [FormattedValuesTransformer,
                AnnotationsTransformer]


def transform(code):
    tree = ast.parse(code)
    for transformer in transformers:
        transformer().visit(tree)
    return unparse(tree)
