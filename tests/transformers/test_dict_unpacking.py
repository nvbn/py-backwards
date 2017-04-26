import pytest
from py_backwards.transformers.dict_unpacking import DictUnpackingTransformer
from ..utils import transform, run


@pytest.mark.parametrize('before, after', [
    ('{1: 2, **{3: 4}}',
     '_py_backwards_merge_dicts([{1: 2}, dict({3: 4})])'),
    ('{**x}', '_py_backwards_merge_dicts([dict(x)])'),
    ('{1: 2, **a, 3: 4, **b, 5: 6}',
     '_py_backwards_merge_dicts([{1: 2}, dict(a), {3: 4}, dict(b), {5: 6}])')])
def test_transform(before, after):
    code = transform(DictUnpackingTransformer, before)
    assert code.split('\n')[-1] == after


@pytest.mark.parametrize('code, result', [
    ('{1: 2, **{3: 4}}', {1: 2, 3: 4}),
    ('{**{5: 6}}', {5: 6}),
    ('{1: 2, **{7: 8}, 3: 4, **{9: 10}, 5: 6}',
     {1: 2, 7: 8, 3: 4, 9: 10, 5: 6})])
def test_run(code, result):
    assert run(DictUnpackingTransformer, code) == result
