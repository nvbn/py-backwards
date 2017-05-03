from typed_ast import ast3 as ast
from ..utils.tree import get_closest_parent_of
from ..utils.helpers import warn
from ..exceptions import NodeNotFound
from .base import BaseNodeTransformer


class SuperWithoutArgumentsTransformer(BaseNodeTransformer):
    """Compiles:
        super()
    To:
        super(Cls, self)
        super(Cls, cls)
            
    """
    target = (2, 7)

    def _replace_super_args(self, node: ast.Call) -> None:
        try:
            func = get_closest_parent_of(self._tree, node, ast.FunctionDef)
        except NodeNotFound:
            warn('super() outside of function')
            return

        try:
            cls = get_closest_parent_of(self._tree, node, ast.ClassDef)
        except NodeNotFound:
            warn('super() outside of class')
            return

        node.args = [ast.Name(id=cls.name), ast.Name(id=func.args.args[0].arg)]

    def visit_Call(self, node: ast.Call) -> ast.Call:
        if isinstance(node.func, ast.Name) and node.func.id == 'super' and not len(node.args):
            self._replace_super_args(node)
            self._tree_changed = True

        return self.generic_visit(node)  # type: ignore
