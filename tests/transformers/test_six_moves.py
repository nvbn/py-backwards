import pytest
from py_backwards.transformers.six_moves import SixMovesTransformer


@pytest.mark.parametrize('before, after', [
    ('from functools import reduce',
     '''
try:
    from functools import reduce
except ImportError:
    from six.moves import reduce as reduce
     '''),
    ('from shlex import quote',
     '''
try:
    from shlex import quote
except ImportError:
    from six.moves import shlex_quote as quote
     '''),
    ('from itertools import zip_longest',
     '''
try:
    from itertools import zip_longest
except ImportError:
    from six.moves import zip_longest as zip_longest
     '''),
    ('from urllib.request import Request, pathname2url',
     '''
try:
    from urllib.request import Request, pathname2url
except ImportError:
    from six.moves.urllib.request import Request as Request
    from six.moves.urllib.request import pathname2url as pathname2url
     ''')])
def test_transform(transform, ast, before, after):
    code = transform(SixMovesTransformer, before)
    assert ast(code) == ast(after)
