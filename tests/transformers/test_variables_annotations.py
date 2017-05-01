import pytest
from py_backwards.transformers.variables_annotations import VariablesAnnotationsTransformer


@pytest.mark.parametrize('before, after', [
    ('a: int = 10', 'a = 10 # type: int'),
    ('a: int', '')])
def test_transform(transform, before, after):
    assert transform(VariablesAnnotationsTransformer, before) == after


@pytest.mark.parametrize('code, result', [
    ('a: int = 10; a', 10),
    ('a: int; "a" in locals()', False)])
def test_run(run_transformed, code, result):
    assert run_transformed(VariablesAnnotationsTransformer, code) == result
