import pytest
from py_backwards.transformers.variables_annotations import VariablesAnnotationsTransformer


@pytest.mark.parametrize('before, after', [
    ('a: int = 10', 'a = 10'),
    ('a: int', '')])
def test_transform(transform, ast, before, after):
    code = transform(VariablesAnnotationsTransformer, before)
    assert ast(after) == ast(code)


@pytest.mark.parametrize('code, result', [
    ('a: int = 10; a', 10),
    ('a: int; "a" in locals()', False)])
def test_run(run_transformed, code, result):
    assert run_transformed(VariablesAnnotationsTransformer, code) == result
