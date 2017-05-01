from typed_ast import ast3 as ast
from typed_astunparse import unparse
from py_backwards.utils.snippet import snippet
from py_backwards.utils.tree import (get_parent, get_non_exp_parent_and_index,
                                     find, insert_at, replace_at)


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


@snippet
def to_insert():
    print(10)


def test_insert_at():
    tree = ast.parse('''
def fn():
    print('hi there')
    ''')

    insert_at(0, tree.body[0], to_insert.get_body())
    expected_code = '''
def fn():
    print(10)
    print('hi there')
    '''
    assert unparse(tree).strip() == expected_code.strip()


def test_replace_at():
    tree = ast.parse('''
def fn():
    print('hi there')
    ''')

    replace_at(0, tree.body[0], to_insert.get_body())
    expected_code = '''
def fn():
    print(10)
    '''
    assert unparse(tree).strip() == expected_code.strip()
