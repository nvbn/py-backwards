import pytest
from py_backwards.transformers.formatted_values import FormattedValuesTransformer


@pytest.mark.parametrize('before, after', [
    ("f'hi'", "'hi'"),
    ("f'hi {x}'", "'hi ' + '{}'.format(x)"),
    ("d = f'{a} {b}!'", "d = '{}'.format(a) + ' ' + '{}'.format(b) + '!'"),
    ("f'hi {x.upper()} {y:1}'",
     "'hi ' + '{}'.format(x.upper()) + ' ' + '{:1}'.format(y)")])
def test_transform(transform, ast, before, after):
    code = transform(FormattedValuesTransformer, before)
    assert ast(code) == ast(after)


@pytest.mark.parametrize('code, result', [
    ("f'hi'", 'hi'),
    ("x = 12; f'hi {x}'", 'hi 12'),
    ("x = 'everyone'; y = 42; f'hi {x.upper()!r} {y:x}'",
     'hi EVERYONE 2a')])
def test_run(run_transformed, code, result):
    assert run_transformed(FormattedValuesTransformer, code) == result
