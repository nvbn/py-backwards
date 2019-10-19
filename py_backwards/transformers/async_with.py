from ..exceptions import NodeNotFound
from ..utils.helpers import warn
from ..utils.snippet import snippet
from ..utils.tree import get_node_position, find, insert_at, replace_at
from ..types import TransformationResult
from .. import ast
from .base import BaseTransformer
from typing import List, Union

@snippet
def _async_with(expr, aenter):
    let(mgr)
    let(aexit)
    let(exc)
    mgr = expr
    aexit = type(mgr).__aexit__
    extend(aenter)
    try:
        ...
    except BaseException as exc:
        if not (yield from aexit(mgr, type(exc), exc, exc.__traceback__)):
            raise
    else:
        aexit(mgr, None, None, None)

    del mgr, aexit

@snippet
def _aenter1(var):
    var = yield from type(mgr).__aenter__(mgr)

@snippet
def _aenter2():
    yield from type(mgr).__aenter__(mgr)

class AsyncWithTransformer(BaseTransformer):
    """Compiles:
        async with test1():
            ...
    """
    target = (3, 4)

    @classmethod
    def _replace_with(cls, tree: ast.AST, node: ast.AsyncWith) -> None:
        try:
            position = get_node_position(tree, node)
        except NodeNotFound:
            warn('Async with outside of body')
            return

        item = node.items[0]
        with_body = node.body # type: List[ast.stmt]
        if len(node.items) > 1:
            with_body = [ast.AsyncWith(items=node.items[1:],
                                       body=with_body)]

        if item.optional_vars:
            aenter = _aenter1.get_body(var=item.optional_vars)
        else:
            aenter = _aenter2.get_body()

        body = _async_with.get_body(expr=item.context_expr, aenter=aenter)
        for n in body:
            if isinstance(n, ast.Try):
                n.body = with_body
                break

        replace_at(position.index, position.parent, body)

        if len(node.items) > 1:
            cls._replace_with(tree, with_body[0]) # type: ignore

    @classmethod
    def transform(cls, tree: ast.AST) -> TransformationResult:
        tree_changed = False

        for node in find(tree, ast.AsyncWith):
            tree_changed = True
            cls._replace_with(tree, node)

        return TransformationResult(tree, tree_changed, []) #['asyncio'])
