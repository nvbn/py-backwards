from typed_ast import ast3 as ast
from astunparse import unparse
from autopep8 import fix_code


class FormattedValuesTransformer(ast.NodeTransformer):
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
                             args=[ast.List(elts=node.values, ctx=ast.Load())],
                             keywords=[])
        return self.generic_visit(join_call)


class FunctionsAnnotationsTransformer(ast.NodeTransformer):
    target = (2, 7)

    def visit_arg(self, node):
        node.annotation = None
        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        node.returns = None
        return self.generic_visit(node)


class VariablesAnnotationsTransformer(ast.NodeTransformer):
    target = (3, 5)

    def visit_AnnAssign(self, node):
        if node.value is None:
            return

        return self.generic_visit(ast.Assign(targets=[node.target],
                                             value=node.value))


transformers = [FormattedValuesTransformer,
                FunctionsAnnotationsTransformer,
                VariablesAnnotationsTransformer]


def transform(code, target):
    tree = ast.parse(code)
    for transformer in transformers:
        if transformer.target >= target:
            transformer().visit(tree)
    return fix_code(unparse(tree))
