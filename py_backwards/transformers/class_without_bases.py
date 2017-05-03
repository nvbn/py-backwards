from typed_ast import ast3 as ast
from .base import BaseNodeTransformer


class ClassWithoutBasesTransformer(BaseNodeTransformer):
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
            self._tree_changed = True

        return self.generic_visit(node)  # type: ignore
