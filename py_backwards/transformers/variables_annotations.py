from typed_ast import ast3 as ast
from .base import BaseTransformer


class VariablesAnnotationsTransformer(BaseTransformer):
    target = (3, 5)

    def visit_AnnAssign(self, node):
        if node.value is None:
            return

        return self.generic_visit(ast.Assign(targets=[node.target],
                                             value=node.value))
