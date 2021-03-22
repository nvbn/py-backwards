import pytest
from py_backwards.utils.helpers import VariablesGenerator
from py_backwards.transformers.python2_future import Python2FutureTransformer


@pytest.mark.parametrize('before, after', [
    ('print(10)', r'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

try:
    input, range, str, bytes, chr = raw_input, xrange, unicode, str, unichr
except NameError:
    pass
else:
    from itertools import ifilter as filter, imap as map, izip as zip

    import itertools as _py_backwards_i_0
    _py_backwards_i_0.filterfalse, \
        _py_backwards_i_0.zip_longest = \
        _py_backwards_i_0.ifilterfalse, \
        _py_backwards_i_0.izip_longest
    del _py_backwards_i_0

print(10)
    '''),
    ('a = 1', r'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

try:
    input, range, str, bytes, chr = raw_input, xrange, unicode, str, unichr
except NameError:
    pass
else:
    from itertools import ifilter as filter, imap as map, izip as zip

    import itertools as _py_backwards_i_0
    _py_backwards_i_0.filterfalse, \
        _py_backwards_i_0.zip_longest = \
        _py_backwards_i_0.ifilterfalse, \
        _py_backwards_i_0.izip_longest
    del _py_backwards_i_0

a = 1
    ''')])
def test_transform(transform, ast, before, after):
    VariablesGenerator._counter = 0
    code = transform(Python2FutureTransformer, before)
    assert ast(code) == ast(after)
