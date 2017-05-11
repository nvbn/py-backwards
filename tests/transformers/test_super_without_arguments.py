import pytest
from py_backwards.transformers.super_without_arguments import SuperWithoutArgumentsTransformer


@pytest.mark.parametrize('before, after', [
    ('''
class A:

    def method(self, x):
        return super().method(x)
    ''', '''
class A():

    def method(self, x):
        return super(A, self).method(x)
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
        return super(A, cls).method(x)
    ''')])
def test_transform(transform, ast, before, after):
    code = transform(SuperWithoutArgumentsTransformer, before)
    assert ast(code) == ast(after)


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
def test_run(run_transformed, code, result):
    assert run_transformed(SuperWithoutArgumentsTransformer, code) == result
