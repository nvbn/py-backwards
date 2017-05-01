from weakref import WeakKeyDictionary
from typing import Tuple, Iterable, Type, TypeVar, Union, List
from typed_ast import ast3 as ast
from ..exceptions import NodeNotFound

_parents = WeakKeyDictionary()  # type: WeakKeyDictionary[ast.AST, ast.AST]


def _build_parents(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            _parents[child] = node


def get_parent(tree: ast.AST, node: ast.AST, rebuild: bool = False) -> ast.AST:
    """Get parrent of node in tree."""
    if node not in _parents or rebuild:
        _build_parents(tree)

    try:
        return _parents[node]
    except IndexError:
        raise NodeNotFound('Parent for {} not found'.format(node))


def get_non_exp_parent_and_index(tree: ast.AST, node: ast.AST) \
        -> Tuple[ast.AST, int]:
    """Get non-Exp parent and index of child."""
    parent = get_parent(tree, node)

    while not hasattr(parent, 'body'):
        node = parent
        parent = get_parent(tree, parent)

    return parent, parent.body.index(node)  # type: ignore


T = TypeVar('T', bound=ast.AST)


def find(tree: ast.AST, type_: Type[T]) -> Iterable[T]:
    """Finds all nodes with type T."""
    for node in ast.walk(tree):
        if isinstance(node, type_):
            yield node  # type: ignore


def insert_at(index: int, parent: ast.AST,
              nodes: Union[ast.AST, List[ast.AST]]) -> None:
    """Inserts nodes to parents body at index."""
    if not isinstance(nodes, list):
        nodes = [nodes]

    for child in nodes[::-1]:
        parent.body.insert(index, child)  # type: ignore


def replace_at(index: int, parent: ast.AST,
               nodes: Union[ast.AST, List[ast.AST]]) -> None:
    """Replaces node in parents body at index with nodes."""
    parent.body.pop(index)  # type: ignore
    insert_at(index, parent, nodes)


def get_closest_parent_of(tree: ast.AST, node: ast.AST,
                          type_: Type[T]) -> T:
    """Get a closest parent of passed type."""
    parent = node

    while True:
        parent = get_parent(tree, parent)

        if isinstance(parent, type_):
            return parent  # type: ignore
