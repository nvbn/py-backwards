from weakref import WeakKeyDictionary
from typing import Tuple, Iterable, Type, TypeVar
from typed_ast import ast3 as ast

_parents = WeakKeyDictionary()  # type: WeakKeyDictionary[ast.AST, ast.AST]


def _build_parents(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            _parents[child] = node


def get_parent(tree: ast.AST, node: ast.AST, rebuild: bool = False) -> ast.AST:
    """Get parrent of node in tree."""
    if node not in _parents or rebuild:
        _build_parents(tree)

    return _parents[node]


def get_non_exp_parent_and_index(tree: ast.AST, node: ast.AST) \
        -> Tuple[ast.AST, int]:
    """Get non-Exp parent and index of child."""
    parent = get_parent(tree, node)

    if not hasattr(parent, 'body'):
        node = parent
        parent = get_parent(tree, node)

    return parent, parent.body.index(node)  # type: ignore


T = TypeVar('T', bound=ast.AST)


def find(tree: ast.AST, type_: Type[T]) -> Iterable[T]:
    """Finds all nodes with type T."""
    for node in ast.walk(tree):
        if isinstance(node, type_):
            yield node  # type: ignore
