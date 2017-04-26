import pytest
from py_backwards.transformers.python2_future import Python2FutureTransformer
from ..utils import transform, run


@pytest.mark.parametrize('before, after', [
    ('print(10)', '''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
print(10)
    '''),
    ('a = 1', '''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
a = 1
    ''')])
def test_transform(before, after):
    assert transform(Python2FutureTransformer, before) == after.strip()
