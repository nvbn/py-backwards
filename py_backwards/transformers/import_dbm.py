from typing import Union
from typed_ast import ast3 as ast
from ..utils.snippet import snippet, extend
from .base import BaseImportRewrite


@snippet
def import_rewrite(previous, current):
    if __import__('six').PY2:
        extend(current)
    else:
        extend(previous)


class ImportDbmTransformer(BaseImportRewrite):
    """Replaces:
    
        dbm => anydbm
        dbm.ndbm => dbm

    """
    target = (2, 7)
    rewrites = [('dbm.ndbm', 'dbm'),
                ('dbm', 'anydbm')]
    wrapper = import_rewrite
    dependencies = ['six']

    def visit_Import(self, node: ast.Import) -> Union[ast.Import, ast.Try]:
        if node.names[0].name == 'dbm' and node.names[0].asname == 'ndbm':
            return node

        return super().visit_Import(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Union[ast.ImportFrom, ast.Try, ast.AST]:
        names = [name.name for name in node.names]
        if node.module == 'dbm' and names == ['ndbm']:
            import_ = ast.Import(names=[ast.alias(name='dbm',
                                                  asname='ndbm')])
            return self.wrapper.get_body(previous=node, current=import_)[0]  # type: ignore

        return super().visit_ImportFrom(node)
