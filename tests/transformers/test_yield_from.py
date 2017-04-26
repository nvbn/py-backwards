import pytest
from py_backwards.transformers.yield_from import YieldFromTransformer
from ..utils import transform, run


@pytest.mark.parametrize('before, after', [
    ('''
def fn():
    yield from range(10)
    ''', '''
def fn():
    _py_backwards_generator_0 = range(10)
    if (not hasattr(_py_backwards_generator_0, '__next__')):
        _py_backwards_generator_0 = iter(_py_backwards_generator_0)
    while True:
        try:
            (yield _py_backwards_generator_0.__next__())
        except StopIteration as _py_backwards_generator_exception_0:
            break
'''),
    ('''
def fn():
    a = yield from range(10)
    ''', '''
def fn():
    _py_backwards_generator_0 = range(10)
    if (not hasattr(_py_backwards_generator_0, '__next__')):
        _py_backwards_generator_0 = iter(_py_backwards_generator_0)
    while True:
        try:
            (yield _py_backwards_generator_0.__next__())
        except StopIteration as _py_backwards_generator_exception_0:
            if hasattr(_py_backwards_generator_exception_0, 'value'):
                a = _py_backwards_generator_exception_0.value
            break
'''),
])
def test_transform(before, after):
    assert transform(YieldFromTransformer, before) == after.strip()


@pytest.mark.parametrize('code, result', [
    ('''
def fn():
    yield from range(3)

list(fn())
    ''', [0, 1, 2]),
    ('''
def fn():
    def fake_gen():
        yield 0
        exc = StopIteration()
        exc.value = 5
        raise exc

    x = yield from fake_gen()
    yield x
    
list(fn())''', [0, 5])])
def test_run(code, result):
    assert run(YieldFromTransformer, code) == result
