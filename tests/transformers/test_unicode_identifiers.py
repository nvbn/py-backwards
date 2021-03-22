import pytest
from py_backwards.transformers.unicode_identifiers import UnicodeIdentifierTransformer
from py_backwards.utils.helpers import eager

# Get a list of variable names to use
def _get_varnames():
    for underscores in ('', '_', '__'):
        for base in ('a', 'a.b'):
            for c, d in (('', ''), ('ċ',
                                    'Xlatin_small_letter_c_with_dot_aboveX')):
                name = underscores + base + c
                if c:
                    expected = underscores + 'hy_' + base + d
                else:
                    expected = underscores + base + d
                yield (name, expected)

# Get a list of things to try
@eager
def _get_tests():
    for name, expected in _get_varnames():
        name1 = name.replace('.', '_')
        expected1 = expected.replace('.', '_')
        for test in ('{0} = 1', 'print({0})', '{0}.c', 'from test import {1}',
                     'def test(a, b{1}, c): pass', 'class test{1}: pass',
                     'try:\n 1/0\nexcept Exception as {1}:\n pass',
                     'import {0}', 'from {0} import {1} as {0}'):
            yield (test.format(name, name1), test.format(expected, expected1))
            return

@pytest.mark.parametrize('before, after', _get_tests())
def test_transform(transform, ast, before, after):
    code = transform(UnicodeIdentifierTransformer, before)

    print(code, 'vs', after)
    assert ast(code) == ast(after)
