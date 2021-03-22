from ..exceptions import NodeNotFound
from ..utils.helpers import warn
from ..utils.snippet import snippet
from ..utils.tree import get_node_position, find, insert_at, replace_at
from ..types import TransformationResult
from .. import ast
from .base import BaseTransformer

# Create a StopAsyncIteration if one doesn't already exist.
@snippet
def _init():
    try:
        assert issubclass(StopAsyncIteration, Exception)
    except (AssertionError, NameError):
        let(builtin)
        import builtins as builtin
        class StopAsyncIteration(Exception):
            pass
        builtin.StopAsyncIteration = StopAsyncIteration
        del builtin

    from asyncio import iscoroutine as _py_backwards_iscoroutine

@snippet
def _async_for(target, iter_):
    let(it)
    let(itertype)
    let(running)
    it = iter_
    it = type(it).__aiter__(it)

    # Support legacy iterators
    if _py_backwards_iscoroutine(it):
        it = yield from it

    itertype = type(it)
    running = True
    while running:
        try:
            target = yield from itertype.__anext__(it)
        except StopAsyncIteration:
            running = False

    del it, itertype, running

class AsyncForTransformer(BaseTransformer):
    """Compiles:
        async def test1():
            async for i in async_iterable:
                print(i)
            else:
                print('Else')
    """
    target = (3, 4)

    @classmethod
    def transform(cls, tree: ast.AST, *, add_init=True) \
            -> TransformationResult:
        tree_changed = False

        for node in find(tree, ast.AsyncFor):
            if not tree_changed:
                tree_changed = True
                if add_init:
                    insert_at(0, tree, _init.get_body())

            try:
                position = get_node_position(tree, node)
            except NodeNotFound:
                warn('Async for outside of body')
                continue

            body = _async_for.get_body(target=node.target, iter_=node.iter)

            # This can't use extend() as that replaces variables.
            for n in body:
                if isinstance(n, ast.While):
                    n.orelse = node.orelse
                    assert isinstance(n.body[0], ast.Try)
                    n.body[0].orelse = node.body
                    break

            replace_at(position.index, position.parent, body)

        return TransformationResult(tree, tree_changed, []) #['asyncio'])
