from typed_ast import ast3 as ast
from astunparse import unparse
from py_backwards.utils.snippet import (snippet, let, find_variables,
                                        VariablesReplacer, extend_tree)


def test_variables_finder():
    tree = ast.parse('''
let(a)
x = 1
let(b)
    ''')
    assert find_variables(tree) == ['a', 'b']


def test_variables_replacer():
    tree = ast.parse('''
from f.f import f as f
import f as f

class f(f):
    def f(f):
        f = f
        for f in f:
            with f as f:
                yield f
        return f

    ''')
    VariablesReplacer.replace(tree, {'f': 'x'})
    code = unparse(tree)

    expected = '''
from x.x import x as x
import x as x

class x(x):

    def x(x):
        x = x
        for x in x:
            with x as x:
                (yield x)
        return x
    '''

    assert code.strip() == expected.strip()


@snippet
def to_extend():
    y = 5


def test_extend_tree():
    tree = ast.parse('''
x = 1
extend(y)
    ''')
    extend_tree(tree, {'y': to_extend.get_body()})
    code = unparse(tree)
    expected = '''
x = 1
y = 5
    '''
    assert code.strip() == expected.strip()


@snippet
def my_snippet(class_name, x_value):
    class class_name:
        pass

    let(x)
    x = x_value

    let(result)
    result = 0

    let(i)
    for i in range(x):
        result += i

    return result


initial_code = '''
def fn():
    pass
    
result = fn()
'''

expected_code = '''
def fn():
    pass

    class MyClass():
        pass
    _py_backwards_x_0 = 10
    _py_backwards_result_1 = 0
    for _py_backwards_i_2 in range(_py_backwards_x_0):
        _py_backwards_result_1 += _py_backwards_i_2
    return _py_backwards_result_1
result = fn()
'''


def _get_code():
    tree = ast.parse(initial_code)
    tree.body[0].body.extend(my_snippet.get_body(class_name='MyClass',
                                                 x_value=ast.Num(10)))
    return unparse(tree)


def test_snippet_code():
    new_code = _get_code()
    assert new_code.strip() == expected_code.strip()


def test_snippet_run():
    new_code = _get_code()
    locals_ = {}
    exec(new_code, {}, locals_)
    assert locals_['result'] == 45
