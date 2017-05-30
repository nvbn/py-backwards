import pytest
from py_backwards.transformers.string_types import StringTypesTransformer


@pytest.mark.parametrize('before, after', [
    ('str(1)', 'unicode(1)'),
    ('str("hi")', 'unicode("hi")'),
    ('something.str()', 'something.str()')])
def test_transform(transform, ast, before, after):
    code = transform(StringTypesTransformer, before)
    assert ast(code) == ast(after)
