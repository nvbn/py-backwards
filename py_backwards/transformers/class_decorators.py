from .. import ast
from ..types import TransformationResult
from ..utils.tree import find, get_node_position, insert_at
from .base import BaseTransformer

class ClassDecoratorTransformer(BaseTransformer):
    """Compiles:
        @decorator
        class Test:
            pass
    To
        class Test:
            pass

        Test = decorator(Test)

    """
    target = (2, 6)

    @classmethod
    def transform(cls, tree: ast.AST) -> TransformationResult:
        tree_changed = False
        for node in find(tree, ast.ClassDef):
            if not node.decorator_list:
                continue

            tree_changed = True
            pos = get_node_position(tree, node)
            index = pos.index + 1
            value = ast.Name(id=node.name, ctx=ast.Load()) # type: ast.AST
            for decorator in reversed(node.decorator_list):
                value = ast.Call(func=decorator, args=[value], keywords=[])

            insert_at(index, pos.parent, ast.Assign(
                targets=[ast.Name(id=node.name, ctx=ast.Store())],
                value=value))
            node.decorator_list = []

        return TransformationResult(tree, tree_changed, [])
