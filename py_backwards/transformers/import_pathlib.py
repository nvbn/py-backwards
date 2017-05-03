from .base import BaseImportRewrite


class ImportPathlibTransformer(BaseImportRewrite):
    target = (3, 3)
    rewrites = [('pathlib', 'pathlib2')]
    dependencies = ['pathlib2']
