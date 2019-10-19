import re
import unicodedata
from .. import ast
from ..utils.snippet import snippet
from ..utils.tree import insert_at
from .base import BaseNodeTransformer

invalid_identifier = re.compile('[^A-Za-z0-9_\.]')

# def mangle(name: str) -> str:
#     """
#     Mangles variable names using Punycode.
#     Examples:
#         testæ → py_backwards_mangled_test_wra
#         _testœ → _py_backwards_mangled__test_lbb
#         __ætest → __py_backwards_mangled___test_qua
#     """
#     underscores = '_' * min(len(name) - len(name.lstrip('_')), 2)
#     name = invalid_identifier.sub('_', name.encode('punycode').decode('ascii'))
#     return '{}py_backwards_mangled_{}'.format(underscores, name)

def _match(match) -> str:
    char = match.group(0)
    name = unicodedata.name(char, '').lower().replace('-', 'H')
    if not name:
        name = 'U{:x}'.format(ord(char))
    return 'X' + invalid_identifier.sub('_', name) + 'X'

_mangle_re = re.compile('[^A-WYZa-z0-9_]')
def mangle(raw_name: str) -> str:
    """
    Mangles variable names in the same way Hy does.
    https://docs.hylang.org/en/stable/language/syntax.html#mangling
    """

    # Handle names with '.'.
    if '.' in raw_name:
        res = []
        for name in raw_name.split('.'):
            if invalid_identifier.search(name):
                res.append(mangle(name))
            else:
                res.append(name)
        return '.'.join(res)

    name = raw_name.lstrip('_')
    underscores = '_' * (len(raw_name) - len(name))
    return underscores + 'hyx_' + _mangle_re.sub(_match, name)

class UnicodeIdentifierTransformer(BaseNodeTransformer):
    """Compiles:
        a = 1
        æ = 2
        __œ = 3
        os.œ = 4
    To
        a = 1
        hyx_Xlatin_small_letter_aeX = 2
        __hyx_Xlatin_small_ligature_oeX = 3
        os.hyx_Xlatin_small_ligature_oeX = 4
    """
    # Old mangler output:
    #   py_backwards_mangled_6ca = 2
    #   __py_backwards_mangled____fsa = 3
    #   os._py_backwards_mangled_bga = 4
    target = (2, 7)

    def visit_Name(self, node: ast.Name) -> ast.Name:
        if invalid_identifier.search(node.id):
            self._tree_changed = True
            node.id = mangle(node.id)

        return self.generic_visit(node)  # type: ignore

    def visit_Attribute(self, node: ast.Attribute) -> ast.Attribute:
        if invalid_identifier.search(node.attr):
            self._tree_changed = True
            node.attr = mangle(node.attr)

        return self.generic_visit(node)  # type: ignore

    def visit_arg(self, node: ast.arg) -> ast.arg:
        if node.arg is not None and invalid_identifier.search(node.arg):
            self._tree_changed = True
            node.arg = mangle(node.arg)

        return self.generic_visit(node)  # type: ignore

    def visit_keyword(self, node: ast.arg) -> ast.arg:
        if node.arg is not None and invalid_identifier.search(node.arg):
            self._tree_changed = True
            node.arg = mangle(node.arg)

        return self.generic_visit(node)  # type: ignore

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        if invalid_identifier.search(node.name):
            self._tree_changed = True
            node.name = mangle(node.name)

        return self.generic_visit(node)  # type: ignore

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        if invalid_identifier.search(node.name):
            self._tree_changed = True
            node.name = mangle(node.name)

        return self.generic_visit(node)  # type: ignore

    # Used in "from ... import ... [as ...]".
    def visit_alias(self, node: ast.alias) -> ast.alias:
        if invalid_identifier.search(node.name):
            self._tree_changed = True
            node.name = mangle(node.name)
        # getattr(node, 'asname', None) works as well, however mypy complains.
        if hasattr(node, 'asname') and node.asname and \
                invalid_identifier.search(node.asname):
            self._tree_changed = True
            node.asname = mangle(node.asname)

        return self.generic_visit(node)  # type: ignore

    # Mangle Unicode names in "except as" statements
    def visit_Try(self, node: ast.Try) -> ast.Try:
        for handler in node.handlers:
            if handler.name and invalid_identifier.search(handler.name):
                self._tree_changed = True
                handler.name = mangle(handler.name)

        return self.generic_visit(node)  # type: ignore
