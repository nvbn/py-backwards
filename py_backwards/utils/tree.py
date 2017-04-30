from weakref import WeakKeyDictionary
from typed_ast import ast3 as ast

_parents = WeakKeyDictionary()


def _build_parents(tree):
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            _parents[child] = node


def get_parent(tree, node, rebuild=False):
    if node not in _parents or rebuild:
        _build_parents(tree)

    return _parents[node]


def get_non_exp_parent_and_index(tree, node):
    parent = get_parent(tree, node)

    if not hasattr(parent, 'body'):
        node = parent
        parent = get_parent(tree, node)

    return parent, parent.body.index(node)


def find(tree, type_=None):
    for node in ast.walk(tree):
        if type_ is None or isinstance(node, type_):
            yield node
