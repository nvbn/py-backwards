import pytest
from py_backwards.transformers.super_without_arguments import SuperWithoutArgumentsTransformer
from .utils import transform, run


@pytest.mark.parametrize('before, after', [
    ('''
class A:

    def method(self, x):
        return super().method(x)
    ''', '''
class A():

    def method(self, x):
        return super(type(self), self).method(x)
    '''),
    ('''
class A:

    @classmethod
    def method(cls, x):
        return super().method(x)
    ''', '''
class A():

    @classmethod
    def method(cls, x):
        return super(cls, cls).method(x)
    ''')])
def test_transform(before, after):
    assert transform(SuperWithoutArgumentsTransformer, before) == after.strip()


@pytest.mark.parametrize('code, result', [
    ('''
class A:
    def x(self):
        return 5
        
class B(A):
    def x(self):
        return super().x()
        
B().x()    
    ''', 5),
    ('''
class A:
    @classmethod
    def x(cls):
        return 5
        
class B(A):
    @classmethod
    def x(cls):
        return super().x()
        
B.x()    
    ''', 5)])
def test_run(code, result):
    assert run(SuperWithoutArgumentsTransformer, code) == result
