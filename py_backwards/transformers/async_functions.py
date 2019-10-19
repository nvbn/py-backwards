import sys
from ..utils.snippet import snippet
from .. import ast
from .base import BaseNodeTransformer
from typing import Optional

@snippet
def _import():
    from asyncio import coroutine as _py_backwards_coroutine

class AsyncFunctionTransformer(BaseNodeTransformer):
    """Compiles:
        async def test():
            await asyncio.sleep(2)
    To
        @_py_backwards_coroutine
        def test():
            yield from asyncio.sleep(2)

    """
    target = (3, 4)
    # dependencies = ['asyncio']

    def visit_Module(self, node: ast.Module) -> Optional[ast.AST]:
        node.body = _import.get_body() + node.body  # type: ignore
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) \
            -> Optional[ast.AST]:
        self._tree_changed = True
        node.decorator_list.append(ast.Name(id='_py_backwards_coroutine'))
        func = ast.FunctionDef(node.name, node.args, node.body,
                               node.decorator_list, node.returns)

        return self.generic_visit(func)

    def visit_Await(self, node: ast.Await) -> Optional[ast.AST]:
        self._tree_changed = True
        return self.generic_visit(ast.YieldFrom(value=node.value))
