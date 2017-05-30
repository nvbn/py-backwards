from weakref import WeakKeyDictionary
from typing import Iterable, Type, TypeVar, Union, List
from typed_ast import ast3 as ast
from ..types import NodePosition
from ..exceptions import NodeNotFound

_parents = WeakKeyDictionary()  # type: WeakKeyDictionary[ast.AST, ast.AST]


def _build_parents(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            _parents[child] = node


def get_parent(tree: ast.AST, node: ast.AST, rebuild: bool = False) -> ast.AST:
    """Get parent of node in tree."""
    if node not in _parents or rebuild:
        _build_parents(tree)

    try:
        return _parents[node]
    except IndexError:
        raise NodeNotFound('Parent for {} not found'.format(node))


def get_node_position(tree: ast.AST, node: ast.AST) -> NodePosition:
    """Get node position with non-Exp parent."""
    parent = get_parent(tree, node)

    while not hasattr(parent, 'body') and not hasattr(parent, 'orelse'):
        node = parent
        parent = get_parent(tree, parent)

    if node in parent.body:  # type: ignore
        return NodePosition(parent, 'body', parent.body,  # type: ignore
                            parent.body.index(node))  # type: ignore
    else:
        return NodePosition(parent, 'orelse', parent.orelse,  # type: ignore
                            parent.orelse.index(node))  # type: ignore


T = TypeVar('T', bound=ast.AST)


def find(tree: ast.AST, type_: Type[T]) -> Iterable[T]:
    """Finds all nodes with type T."""
    for node in ast.walk(tree):
        if isinstance(node, type_):
            yield node  # type: ignore


def insert_at(index: int, parent: ast.AST,
              nodes: Union[ast.AST, List[ast.AST]],
              holder_attribute='body') -> None:
    """Inserts nodes to parents body at index."""
    if not isinstance(nodes, list):
        nodes = [nodes]

    for child in nodes[::-1]:
        getattr(parent, holder_attribute).insert(index, child)  # type: ignore


def replace_at(index: int, parent: ast.AST,
               nodes: Union[ast.AST, List[ast.AST]],
               holder_attribute='body') -> None:
    """Replaces node in parents body at index with nodes."""
    getattr(parent, holder_attribute).pop(index)  # type: ignore
    insert_at(index, parent, nodes, holder_attribute)


def get_closest_parent_of(tree: ast.AST, node: ast.AST,
                          type_: Type[T]) -> T:
    """Get a closest parent of passed type."""
    parent = node

    while True:
        parent = get_parent(tree, parent)

        if isinstance(parent, type_):
            return parent  # type: ignore
