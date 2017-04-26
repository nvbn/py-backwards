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
    ('def fn(x: T) -> List[T]:\n    return [x]', 'def fn(x):\n    return [x]'),
    ('def fn(x: int) -> float:\n    return 1.5', 'def fn(x):\n    return 1.5'),
])
def test_functions_annotations_transformer(before, after):
    assert _transform(transformers.FunctionsAnnotationsTransformer, before) \
           == after


@pytest.mark.parametrize('before, after', [
    ('a: int = 10', 'a = 10'),
    ('a: int', ''),
])
def test_variables_annotations_transformer(before, after):
    assert _transform(transformers.VariablesAnnotationsTransformer, before) \
           == after


@pytest.mark.parametrize('before, after', [
    ('[1, 2, 3]', '[1, 2, 3]'),
    ('[1, 2, *range(5, 10), 3, 4]',
     '(([1, 2] + list(range(5, 10))) + [3, 4])'),
    ('[*range(5), *range(5, 10)]', '(list(range(5)) + list(range(5, 10)))'),
    ('[*range(5, 10)]', 'list(range(5, 10))'),
    ('print(1, 2, 3)', 'print(1, 2, 3)'),
    ('print(1, 2, *range(5, 10), 3, 4)',
     'print(*(([1, 2] + list(range(5, 10))) + [3, 4]))'),
    ('print(*range(5), *range(5, 10))',
     'print(*(list(range(5)) + list(range(5, 10))))'),
    ('print(*range(5, 10))',
     'print(*list(range(5, 10)))'),
])
def test_starred_unpacking_transformer(before, after):
    assert _transform(transformers.StarredUnpackingTransformer, before) \
           == after


@pytest.mark.parametrize('before, after', [
    ('{1: 2, **{3: 4}}',
     '__py_backwards_merge_dicts([{1: 2}, dict({3: 4})])'),
    ('{**x}', '__py_backwards_merge_dicts([dict(x)])'),
    ('{1: 2, **a, 3: 4, **b, 5: 6}',
     '__py_backwards_merge_dicts([{1: 2}, dict(a), {3: 4}, dict(b), {5: 6}])')
])
def test_dict_unpacking_transformer(before, after):
    assert _transform(transformers.DictUnpackingTransformer, before) \
           == (transformers.merge_dicts_fn + after).strip()
