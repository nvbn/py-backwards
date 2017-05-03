from typed_ast import ast3 as ast
from ..utils.tree import find, get_non_exp_parent_and_index, insert_at
from ..utils.helpers import warn
from ..types import TransformationResult
from ..exceptions import NodeNotFound
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
    def transform(cls, tree: ast.AST) -> TransformationResult:
        tree_changed = False

        for node in find(tree, ast.AnnAssign):
            try:
                parent, index = get_non_exp_parent_and_index(tree, node)
            except NodeNotFound:
                warn('Assignment outside of body')
                continue

            tree_changed = True
            parent.body.pop(index)  # type: ignore

            if node.value is not None:
                insert_at(index, parent,
                          ast.Assign(targets=[node.target],  # type: ignore
                                     value=node.value,
                                     type_comment=node.annotation))

        return TransformationResult(tree, tree_changed, [])
