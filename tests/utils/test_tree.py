from typed_ast import ast3 as ast
from astunparse import unparse
from py_backwards.utils.snippet import snippet
from py_backwards.utils.tree import (get_parent, get_non_exp_parent_and_index,
                                     find, insert_at, replace_at)


def test_get_parent(as_ast):
    @as_ast
    def tree():
        x = 1

    assignment = tree.body[0].body[0]
    assert get_parent(tree, assignment) == tree.body[0]


def test_get_non_exp_parent_and_index(as_ast):
    @as_ast
    def tree():
        x = 1
        print(10)

    call = tree.body[0].body[1].value
    parent, index = get_non_exp_parent_and_index(tree, call)
    assert index == 1
    assert parent == tree.body[0]


def test_find(as_ast):
    @as_ast
    def tree():
        print('hi there')
        print(10)

    calls = list(find(tree, ast.Call))
    assert len(calls) == 2


@snippet
def to_insert():
    print(10)


def test_insert_at(as_ast, as_str):
    def fn():
        print('hi there')

    tree = as_ast(fn)
    insert_at(0, tree.body[0], to_insert.get_body())

    def fn():
        print(10)
        print('hi there')

    expected_code = as_str(fn)
    assert unparse(tree).strip() == expected_code


def test_replace_at(as_ast, as_str):
    def fn():
        print('hi there')

    tree = as_ast(fn)
    replace_at(0, tree.body[0], to_insert.get_body())

    def fn():
        print(10)

    expected_code = as_str(fn)
    assert unparse(tree).strip() == expected_code
