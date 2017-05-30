from typed_ast import ast3 as ast
from astunparse import unparse
from py_backwards.utils.snippet import snippet
from py_backwards.utils.tree import (get_parent, get_node_position,
                                     find, insert_at, replace_at)


def test_get_parent(as_ast):
    @as_ast
    def tree():
        x = 1

    assignment = tree.body[0].body[0]
    assert get_parent(tree, assignment) == tree.body[0]


class TestGetNodePosition:
    def test_from_body(self, as_ast):
        @as_ast
        def tree():
            x = 1
            print(10)

        call = tree.body[0].body[1].value
        position = get_node_position(tree, call)
        assert position.index == 1
        assert position.parent == tree.body[0]
        assert position.attribute == 'body'

    def test_from_orelse(self, as_ast):
        @as_ast
        def tree():
            if True:
                print(0)
            else:
                print(1)

        call = tree.body[0].body[0].orelse[0].value
        position = get_node_position(tree, call)
        assert position.index == 0
        assert position.parent == tree.body[0].body[0]
        assert position.attribute == 'orelse'


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
