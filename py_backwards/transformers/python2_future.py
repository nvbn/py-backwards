from typing import List
from typed_ast import ast3 as ast
from .base import BaseTransformer


class Python2FutureTransformer(BaseTransformer):
    """Prepends module with:
        from __future__ import absolute_import
        from __future__ import division
        from __future__ import print_function
            
    """
    target = (2, 7)

    def _get_imports(self) -> List[ast.stmt]:
        return [ast.ImportFrom(
            module='__future__',
            names=[ast.alias(
                name='absolute_import',
                asname=None)],
            level=0),
            ast.ImportFrom(
                module='__future__',
                names=[ast.alias(
                    name='division',
                    asname=None)],
                level=0),
            ast.ImportFrom(
                module='__future__',
                names=[ast.alias(
                    name='print_function',
                    asname=None)],
                level=0)]

    def visit_Module(self, node: ast.Module) -> ast.Module:
        node.body = self._get_imports() + node.body
        return super().visit_Module(node)
