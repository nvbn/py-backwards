from typed_ast import ast3 as ast
from ..utils.snippet import snippet
from .base import BaseNodeTransformer


@snippet
def imports(future):
    from future import absolute_import
    from future import division
    from future import print_function
    from future import unicode_literals


class Python2FutureTransformer(BaseNodeTransformer):
    """Prepends module with:
        from __future__ import absolute_import
        from __future__ import division
        from __future__ import print_function
        from __future__ import unicode_literals
            
    """
    target = (2, 7)

    def visit_Module(self, node: ast.Module) -> ast.Module:
        self._tree_changed = True
        node.body = imports.get_body(future='__future__') + node.body  # type: ignore
        return self.generic_visit(node)  # type: ignore
