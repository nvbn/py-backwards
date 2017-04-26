import pytest
from py_backwards.transformers.class_without_bases import ClassWithoutBasesTransformer
from ..utils import transform, run


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
def test_transform(before, after):
    assert transform(ClassWithoutBasesTransformer, before) == after.strip()
