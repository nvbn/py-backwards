from typed_ast import ast3 as ast
from py_backwards.utils.tree import (get_parent, get_non_exp_parent_and_index,
                                     find)


def test_get_parent():
    tree = ast.parse('''
def fn():
    x = 1
    ''')
    assignment = tree.body[0].body[0]
    assert get_parent(tree, assignment) == tree.body[0]


def test_get_non_exp_parent_and_index():
    tree = ast.parse('''
def fn():
    x = 1
    print(10)
    ''')
    call = tree.body[0].body[1].value
    parent, index = get_non_exp_parent_and_index(tree, call)
    assert index == 1
    assert parent == tree.body[0]


def test_find():
    tree = ast.parse('''
def fn():
    print('hi there')
    print(10)
    ''')
    calls = list(find(tree, ast.Call))
    assert len(calls) == 2
