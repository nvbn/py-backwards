import pytest
from py_backwards.transformers.class_without_bases import ClassWithoutBasesTransformer


@pytest.mark.parametrize('before, after', [
    ('''
class A:
    pass
    ''', '''
class A(object):
    pass
    '''),
    ('''
class A():
    pass
    ''', '''
class A(object):
    pass
    ''')])
def test_transform(transform, ast, before, after):
    code = transform(ClassWithoutBasesTransformer, before)
    assert ast(code) == ast(after)
