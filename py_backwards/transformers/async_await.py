from typed_ast import ast3 as ast
from .base import BaseNodeTransformer

def asyncio_decorator():
    return ast.Attribute(
        value=ast.Name(
            id='asyncio',
            ctx=ast.Load(),
        ),
        attr='coroutine',
    )


class AsyncAwaitTransformer(BaseNodeTransformer):
    """Compiles:
        async def ham():
            await foo()
    To

        import asyncio

        @asyncio.coroutine
        def ham():
            yield from foo()
    """
    target = (3, 4)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.FunctionDef:
        self._tree_changed = True
        return self.generic_visit(ast.FunctionDef(
            name=node.name,
            args=node.args,
            body=node.body,
            decorator_list=node.decorator_list + [asyncio_decorator()],
            returns=node.returns,
        ))

    def visit_Await(self, node: ast.Await) -> ast.Await:
        self._tree_changed = True
        return self.generic_visit(ast.YieldFrom(value=node.value))
