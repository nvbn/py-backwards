import pytest
from py_backwards.transformers.variables_annotations import VariablesAnnotationsTransformer
from .utils import transform, run


@pytest.mark.parametrize('before, after', [
    ('a: int = 10', 'a = 10'),
    ('a: int', '')])
def test_transform(before, after):
    assert transform(VariablesAnnotationsTransformer, before) == after


@pytest.mark.parametrize('code, result', [
    ('a: int = 10; a', 10),
    ('a: int; "a" in locals()', False)])
def test_run(code, result):
    assert run(VariablesAnnotationsTransformer, code) == result
