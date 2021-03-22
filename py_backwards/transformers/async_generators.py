from ..types import TransformationResult
from ..utils.snippet import snippet
from ..utils.tree import insert_at
from .. import ast
from .async_for import AsyncForTransformer
from .async_with import AsyncWithTransformer
from .base import BaseNodeTransformer
from typing import List, Tuple, Optional, Union

# Handle generators.
@snippet
def _async_generator():
    let(coro)
    let(AsyncGenerator)
    from asyncio import (coroutine as coro,
                         iscoroutine as _py_backwards_iscoroutine)
    class AsyncGenerator:
        __slots__ = ('_iter', 'ag_running')

        @coro
        def asend(self, value):
            while True:
                try:
                    i = self._iter.send(value)
                except StopIteration:
                    self.ag_running = False
                    raise StopAsyncIteration from None

                # Normally, isinstance would be used, however a tuple subclass
                #   should never be yield-ed when being used as a generator
                #   yield.
                if type(i) is tuple and len(i) == 2 and \
                        i[0] is _py_backwards_async_generator:
                    return i[1]

                value = yield i

        # I think athrow() and aclose() are implemented correctly here, however
        #   they are probably not.
        @coro
        def athrow(self, *args):
            if not self.ag_running:
                return

            i = self._iter.throw(*args)
            if type(i) is tuple and len(i) == 2 and \
                    i[0] is _py_backwards_async_generator:
                return i[1]

            return (yield from self.asend((yield i)))

        @coro
        def aclose(self):
            try:
                yield from self.athrow(GeneratorExit)
            except StopAsyncIteration:
                pass

        def __aiter__(self):
            return self

        @coro
        def __anext__(self):
            return (yield from self.asend(None))

        def __init__(self, iterator):
            self._iter = iterator
            self.ag_running = True

    let(functools_wraps)
    from functools import wraps as functools_wraps

    def _py_backwards_async_generator(func):
        @functools_wraps(func)
        def wrapper(*args, **kwargs):
            return AsyncGenerator(coro_func(*args, **kwargs))
        coro_func = coro(func)
        return wrapper

class _YieldFinder(ast.NodeVisitor):
    @classmethod
    def find_yields(cls, tree: ast.AsyncFunctionDef) \
            -> Tuple[List[ast.Yield], List[ast.Await]]:
        self = cls()
        self.generic_visit(tree)
        if self.returns_value and self.yields:
            exc = SyntaxError("'return' with value in async generator")
            exc.ast_node = self.returns_value # type: ignore
            raise exc
        return self.yields, self.awaits

    def __init__(self):
        self.yields = [] # type: List[ast.Yield]
        self.awaits = [] # type: List[ast.Await]
        self.returns_value = None # type: Optional[ast.Return]

    def visit_FunctionDef(self, node: ast.AST) -> ast.AST:
        return node

    visit_ClassDef = visit_Lambda = visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Yield(self, node: ast.Yield) -> ast.AST:
        self.yields.append(node)
        return self.generic_visit(node)

    def visit_Await(self, node: ast.Await) -> ast.AST:
        self.awaits.append(node)
        return self.generic_visit(node)

    def visit_YieldFrom(self, node: ast.YieldFrom) -> ast.AST:
        # Ignore if the name contains _py_backwards.
        n = node.value # type: ast.AST
        if isinstance(n, ast.Call):
            n = n.func
        if isinstance(n, ast.Attribute):
            n = n.value
        if isinstance(n, ast.Name) and n.id.startswith('_py_backwards_it'):
            return self.generic_visit(node)

        # Otherwise raise a SyntaxError.
        exc = SyntaxError('yield from in async function')
        exc.ast_node = node # type: ignore
        raise exc

    def visit_Return(self, node: ast.Return) -> ast.AST:
        if node.value and not self.returns_value:
            self.returns_value = node

        return self.generic_visit(node)

class AsyncGeneratorTransformer(BaseNodeTransformer):
    """Compiles:
        async def test2():
            yield 1
            await asyncio.sleep(1)
            yield 2
    To
        @_py_backwards_async_generator
        def test2():
            yield (_py_backwards_async_generator, 1)
            yield from asyncio.sleep(1)
            yield (_py_backwards_async_generator, 2)
    """
    target = (3, 5)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> \
            Optional[ast.AST]:
        """ Searches for async iterators and rewrites them. """
        yields, awaits = _YieldFinder.find_yields(node)

        if yields:
            # Because this is no longer an async function, "async for" and
            #   "async with" need to be removed.
            AsyncForTransformer.transform(node, add_init=False)
            AsyncWithTransformer.transform(node)

            self._tree_changed = True
            for n in yields:
                name = ast.Name(id='_py_backwards_async_generator',
                                ctx=ast.Load())
                if not n.value:
                    n.value = ast.NameConstant(value=None)
                n.value = ast.Tuple(elts=[name, n.value], ctx=ast.Load())

            name = ast.Name(id='_py_backwards_async_generator', ctx=ast.Load())
            node.decorator_list.append(name)

            for await_ in awaits:
                await_.py_backwards_await = True # type: ignore

            func = ast.FunctionDef(name=node.name, args=node.args,
                                   body=node.body, returns=node.returns,
                                   decorator_list=node.decorator_list)
            return self.generic_visit(func)

        return self.generic_visit(node)

    def visit_Await(self, node: ast.Await) -> Optional[ast.AST]:
        if getattr(node, 'py_backwards_await', False):
            return self.generic_visit(ast.YieldFrom(value=node.value))
        return self.generic_visit(node)

    @classmethod
    def transform(cls, tree: ast.AST) -> TransformationResult:
        res = super().transform(tree)
        if res.tree_changed and \
                isinstance(getattr(res.tree, 'body', None), list):
            insert_at(0, res.tree, _async_generator.get_body())
        return res
