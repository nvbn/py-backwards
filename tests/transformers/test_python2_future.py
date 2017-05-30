import pytest
from py_backwards.transformers.python2_future import Python2FutureTransformer


@pytest.mark.parametrize('before, after', [
    ('print(10)', '''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
print(10)
    '''),
    ('a = 1', '''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
a = 1
    ''')])
def test_transform(transform, ast, before, after):
    code = transform(Python2FutureTransformer, before)
    assert ast(code) == ast(after)
