from typing import Optional
from typed_ast import ast3 as ast
from .base import BaseTransformer


class VariablesAnnotationsTransformer(BaseTransformer):
    """Compiles:
        a: int = 10
        b: int
    To:
        a = 10
    
    """
    target = (3, 5)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> Optional[ast.Assign]:
        if node.value is None:
            return None

        return self.generic_visit(ast.Assign(targets=[node.target],  # type: ignore
                                             value=node.value))
