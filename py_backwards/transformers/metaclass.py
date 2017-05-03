from typed_ast import ast3 as ast
from ..utils.snippet import snippet
from ..utils.tree import insert_at
from .base import BaseNodeTransformer


@snippet
def six_import():
    from six import with_metaclass as _py_backwards_six_withmetaclass


@snippet
def class_bases(metaclass, bases):
    _py_backwards_six_withmetaclass(metaclass, *bases)


class MetaclassTransformer(BaseNodeTransformer):
    """Compiles:
        class A(metaclass=B):
            pass
    To:
        class A(_py_backwards_six_with_metaclass(B))
    
    """
    target = (2, 7)
    dependencies = ['six']

    def visit_Module(self, node: ast.Module) -> ast.Module:
        insert_at(0, node, six_import.get_body())
        return self.generic_visit(node)  # type: ignore

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        if node.keywords:
            metaclass = node.keywords[0].value
            node.bases = class_bases.get_body(metaclass=metaclass,  # type: ignore
                                              bases=ast.List(elts=node.bases))
            node.keywords = []
            self._tree_changed = True

        return self.generic_visit(node)  # type: ignore
