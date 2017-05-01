from typed_ast import ast3 as ast
from ..utils.tree import find, get_non_exp_parent_and_index, insert_at
from .base import BaseTransformer


class VariablesAnnotationsTransformer(BaseTransformer):
    """Compiles:
        a: int = 10
        b: int
    To:
        a = 10

    """
    target = (3, 5)

    @classmethod
    def transform(cls, tree: ast.AST) -> ast.AST:
        for node in find(tree, ast.AnnAssign):
            parent, index = get_non_exp_parent_and_index(tree, node)
            parent.body.pop(index)  # type: ignore

            if node.value is not None:
                insert_at(index, parent,
                          ast.Assign(targets=[node.target],  # type: ignore
                                     value=node.value,
                                     type_comment=node.annotation))

        return tree
