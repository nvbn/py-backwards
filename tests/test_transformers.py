import pytest
from typed_ast import ast3 as ast
from astunparse import unparse
from py_backwards import transformers
from .utils import dump


def _transform(transformer, before):
    tree = ast.parse(before)
    try:
        transformer().visit(tree)
        return unparse(tree).strip()
    except:
        print('Before:')
        print(dump(ast.parse(before)))
        print('After:')
        print(dump(tree))
        raise


@pytest.mark.parametrize('before, after', [
    ("f'hi'", "'hi'"),
    ("f'hi {x}'", "''.join(['hi ', '{}'.format(x)])"),
    ("f'hi {x.upper()} {y:1}'",
     "''.join(['hi ', '{}'.format(x.upper()), ' ', '{:1}'.format(y)])"),
])
def test_formatted_values_transformer(before, after):
    assert _transform(transformers.FormattedValuesTransformer, before) == after


@pytest.mark.parametrize('before, after', [
    ('a: int = 10', 'a = 10'),
    ('a: int', ''),
    ('def fn(x: int) -> float:\n    return 1.5', 'def fn(x):\n    return 1.5'),
])
def test_annotations_transformer(before, after):
    assert _transform(transformers.AnnotationsTransformer, before) == after
