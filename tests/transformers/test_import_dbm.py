import pytest
from py_backwards.transformers.import_dbm import ImportDbmTransformer


@pytest.mark.parametrize('before, after', [
    ('import dbm',
     '''
if __import__('six').PY2:
    import anydbm as dbm
else:
    import dbm
     '''),
    ('from dbm import ndbm',
     '''
if __import__('six').PY2:
    import dbm as ndbm
else:
    from dbm import ndbm
     '''),
    ('from dbm.ndbm import library',
     '''
if __import__('six').PY2:
    from dbm import library
else:
    from dbm.ndbm import library
     ''')])
def test_transform(transform, ast, before, after):
    code = transform(ImportDbmTransformer, before)
    assert ast(code) == ast(after)
