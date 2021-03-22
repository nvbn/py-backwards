from .. import ast
from .base import BaseNodeTransformer


class SetLiteralTransformer(BaseNodeTransformer):
    """Compiles:
        x = {1, 2, 3, 4}
        y = {i * 10 for i in range(10)}
        z = frozenset({1, 2, 3, 4})
        print({1, 2, 3, 4})
    To
        x = set((1, 2, 3, 4))
        y = set(i * 10 for i in range(10))
        z = frozenset((1, 2, 3, 4))
        print(set((1, 2, 3, 4)))

    """
    target = (2, 6)

    def visit_Set(self, node: ast.Set) -> ast.Call:
        self._tree_changed = True

        set_call = ast.Call(func=ast.Name(id='set', ctx=ast.Load()),
                               args=[ast.Tuple(elts=node.elts, ctx=ast.Load())],
                               keywords=[])

        return self.generic_visit(set_call)  # type: ignore

    def visit_SetComp(self, node: ast.SetComp) -> ast.Call:
        self._tree_changed = True

        set_call = ast.Call(func=ast.Name(id='set', ctx=ast.Load()),
            args=[ast.GeneratorExp(elt=node.elt, generators=node.generators)],
            keywords=[])

        return self.generic_visit(set_call)  # type: ignore

    # This is not strictly required, however prevents frozenset({1, 2, 3}) from
    #   calling set().
    def visit_Call(self, node: ast.Call) -> ast.Call:
        if isinstance(node.func, ast.Name) and node.func.id == 'frozenset' \
                and node.args and isinstance(node.args[0], ast.Set):
            self._tree_changed = True
            node.args[0] = ast.Tuple(elts=node.args[0].elts)

        return self.generic_visit(node)  # type: ignore
