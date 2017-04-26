from typed_ast import ast3 as ast
from .base import BaseTransformer


class ClassWithoutBasesTransformer(BaseTransformer):
    """Compiles:
        class A:
            pass
    To:
        class A(object)
    
    """
    target = (2, 7)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        if not node.bases:
            node.bases = [ast.Name(id='object')]

        return self.generic_visit(node)  # type: ignore
