from .base import BaseTransformer


class FunctionsAnnotationsTransformer(BaseTransformer):
    target = (2, 7)

    def visit_arg(self, node):
        node.annotation = None
        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        node.returns = None
        return self.generic_visit(node)
