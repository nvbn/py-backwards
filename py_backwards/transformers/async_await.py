from typed_ast import ast3 as ast
from .base import BaseNodeTransformer


ASYNCIO_MODULE = '__py_backwards_asyncio__'

def asyncio_decorator():
    return ast.Attribute(
        value=ast.Name(
            id=ASYNCIO_MODULE,
            ctx=ast.Load(),
        ),
        attr='coroutine',
    )


def splice(fn, vars):
    for i, v in enumerate(vars):
        nv = fn(v)
        if nv is None:
            yield v
        else:
            yield nv
            for v in vars[i:]:
                yield v
            break


class AsyncAwaitTransformer(BaseNodeTransformer):
    """Compiles:
        async def ham():
            await foo()
    To

        import asyncio as __py_backwards_asyncio__

        @__py_backwards_asyncio__.coroutine
        def ham():
            yield from foo()
    """
    target = (3, 4)

    def visit_Module(self, n: ast.Module) -> ast.Module:
        self._tree_changed = True
        def dosplice(v):
            # insert just after the first node that's not a future import.
            if not (isinstance(v, ast.ImportFrom) and v.module == '__future__'):
                return ast.Import(names=[ast.alias('asyncio', ASYNCIO_MODULE)])

        return self.generic_visit(ast.Module(body=list(splice(dosplice, n.body))))

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
