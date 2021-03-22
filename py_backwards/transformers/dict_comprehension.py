from .. import ast
from .base import BaseNodeTransformer


class DictComprehensionTransformer(BaseNodeTransformer):
    """Compiles:
        d = {v: k for k, v in zip(range(10), range(10, 20))}
    To
        d = dict((v, k) for k, v in zip(range(10), range(10, 20)))

    """
    target = (2, 6)

    def visit_DictComp(self, node: ast.DictComp) -> ast.Call:
        self._tree_changed = True

        generator = ast.GeneratorExp(elt=ast.Tuple(elts=[node.key, node.value]),
                                     generators=node.generators)

        res = ast.Call(func=ast.Name(id='dict'), args=[generator],
                       keywords=[])

        return self.generic_visit(res)  # type: ignore
