from typed_ast import ast3 as ast
from ..types import CompilationTarget


class BaseTransformer(ast.NodeTransformer):
    target = None  # type: CompilationTarget

    def _set_parents(self, tree: ast.AST):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node

    @classmethod
    def transform(cls, tree: ast.AST) -> ast.AST:
        inst = cls()
        inst._set_parents(tree)
        inst.visit(tree)
        return tree
