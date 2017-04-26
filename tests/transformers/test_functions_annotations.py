import pytest
from py_backwards.transformers.functions_annotations import FunctionsAnnotationsTransformer
from ..utils import transform, run


@pytest.mark.parametrize('before, after', [
    ('def fn(x: T) -> List[T]:\n    return [x]',
     'def fn(x):\n    return [x]'),
    ('def fn(x: int) -> float:\n    return 1.5',
     'def fn(x):\n    return 1.5')])
def test_transform(before, after):
    assert transform(FunctionsAnnotationsTransformer, before) == after


@pytest.mark.parametrize('code, result', [
    ('def fn(x: T) -> List[T]:\n    return [x]; fn(10)', [10]),
    ('def fn(x: int) -> float:\n    return 1.5; fn(10)', 1.5)])
def test_run(code, result):
    assert run(FunctionsAnnotationsTransformer, code) == result
