from typing import List
from typed_ast import ast3 as ast
from ..utils.snippet import snippet
from .base import BaseTransformer


@snippet
def imports(future):
    from future import absolute_import
    from future import division
    from future import print_function


class Python2FutureTransformer(BaseTransformer):
    """Prepends module with:
        from __future__ import absolute_import
        from __future__ import division
        from __future__ import print_function
            
    """
    target = (2, 7)

    def visit_Module(self, node: ast.Module) -> ast.Module:
        node.body = imports.get_body(future='__future__') + node.body
        return self.generic_visit(node)
