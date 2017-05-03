from .base import BaseImportRewrite


class ImportPathlibTransformer(BaseImportRewrite):
    """Replaces pathlib with backported pathlib2."""
    target = (3, 3)
    rewrites = [('pathlib', 'pathlib2')]
    dependencies = ['pathlib2']
