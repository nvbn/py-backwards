import pytest
from py_backwards.transformers.import_pathlib import ImportPathlibTransformer


@pytest.mark.parametrize('before, after', [
    ('import pathlib',
     '''
try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib
     '''),
    ('import pathlib as p',
     '''
try:
    import pathlib as p
except ImportError:
    import pathlib2 as p
     '''),
    ('from pathlib import Path',
     '''
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path
     ''')])
def test_transform(transform, ast, before, after):
    code = transform(ImportPathlibTransformer, before)
    assert ast(code) == ast(after)
