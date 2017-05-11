import pytest
from py_backwards.transformers.return_from_generator import ReturnFromGeneratorTransformer


@pytest.mark.parametrize('before, after', [
    ('''
def fn():
    yield 1
    return 5
    ''', '''
def fn():
    (yield 1)
    _py_backwards_exc_0 = StopIteration()
    _py_backwards_exc_0.value = 5
    raise _py_backwards_exc_0
    '''),
    ('''
def fn():
    if True:
        x = yield from [1]
    return 5
    ''', '''
def fn():
    if True:
        x = (yield from [1])
    _py_backwards_exc_0 = StopIteration()
    _py_backwards_exc_0.value = 5
    raise _py_backwards_exc_0
    ''')])
def test_transform(transform, ast, before, after):
    code = transform(ReturnFromGeneratorTransformer, before)
    assert ast(code) == ast(after)


get_value = '''
gen = fn()
next(gen)
val = None
try:
    next(gen)
except StopIteration as e:
    val = e.value
val
'''


@pytest.mark.parametrize('code, result', [
    ('''
def fn():
    yield 1
    return 5
{}
    '''.format(get_value), 5),
    ('''
def fn():
    yield from [1]
    return 6
{}
    '''.format(get_value), 6),
    ('''
def fn():
    x = yield 1
    return 7
{}
    '''.format(get_value), 7),
    ('''
def fn():
    x = yield from [1]
    return 8
{}
    '''.format(get_value), 8)])
def test_run(run_transformed, code, result):
    assert run_transformed(ReturnFromGeneratorTransformer, code) == result
