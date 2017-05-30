from typed_ast import ast3 as ast
from ..utils.tree import find
from ..types import TransformationResult
from .base import BaseTransformer


class StringTypesTransformer(BaseTransformer):
    """Replaces `str` with `unicode`. 

    """
    target = (2, 7)

    @classmethod
    def transform(cls, tree: ast.AST) -> TransformationResult:
        tree_changed = False

        for node in find(tree, ast.Name):
            if node.id == 'str':
                node.id = 'unicode'
                tree_changed = True

        return TransformationResult(tree, tree_changed, [])
