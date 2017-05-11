import pytest
from py_backwards.transformers.metaclass import MetaclassTransformer


@pytest.mark.parametrize('before, after', [
    ('''
class A(metaclass=B):
    pass
    ''', '''
from six import with_metaclass as _py_backwards_six_withmetaclass

class A(
_py_backwards_six_withmetaclass(B, *[])):
    pass
    '''),
    ('''
class A(C, metaclass=B):
    pass
    ''', '''
from six import with_metaclass as _py_backwards_six_withmetaclass

class A(
_py_backwards_six_withmetaclass(B, *[C])):
    pass
    ''')])
def test_transform(transform, ast, before, after):
    code = transform(MetaclassTransformer, before)
    assert ast(code) == ast(after)
