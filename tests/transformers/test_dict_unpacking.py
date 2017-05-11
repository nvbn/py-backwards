import pytest
from py_backwards.transformers.dict_unpacking import DictUnpackingTransformer


prefix = '''
def _py_backwards_merge_dicts(dicts):
    result = {}
    for dict_ in dicts:
        result.update(dict_)
    return result
'''


@pytest.mark.parametrize('before, after', [
    ('{1: 2, **{3: 4}}',
     prefix + '_py_backwards_merge_dicts([{1: 2}, dict({3: 4})])'),
    ('{**x}', prefix + '_py_backwards_merge_dicts([dict(x)])'),
    ('{1: 2, **a, 3: 4, **b, 5: 6}',
     prefix + '_py_backwards_merge_dicts([{1: 2}, dict(a), {3: 4}, dict(b), {5: 6}])')])
def test_transform(transform, ast, before, after):
    code = transform(DictUnpackingTransformer, before)
    assert ast(code) == ast(after)


@pytest.mark.parametrize('code, result', [
    ('{1: 2, **{3: 4}}', {1: 2, 3: 4}),
    ('{**{5: 6}}', {5: 6}),
    ('{1: 2, **{7: 8}, 3: 4, **{9: 10}, 5: 6}',
     {1: 2, 7: 8, 3: 4, 9: 10, 5: 6})])
def test_run(run_transformed, code, result):
    assert run_transformed(DictUnpackingTransformer, code) == result
