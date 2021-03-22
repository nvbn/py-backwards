from .. import ast
from .base import BaseNodeTransformer
from typing import List, Union

def _find_bool(nodes: Union[List[ast.AST], List[ast.expr]]) -> bool:
    for node in nodes:
        if isinstance(node, ast.Name):
            if node.id == '__bool__':
                return True
        elif isinstance(node, ast.Tuple):
            if _find_bool(node.elts):
                return True

    return False

class ClassBoolMethodTransformer(BaseNodeTransformer):
    """Compiles:
        class A:
            def __bool__(self):
                return False
    To:
        class A:
            def __bool__(self):
                return False
            __nonzero__ = __bool__

    """
    target = (2, 7)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        has_bool = False
        for n in node.body:
            if has_bool:
                break

            if isinstance(n, ast.Assign):
                has_bool = _find_bool(n.targets)
            elif isinstance(n, ast.FunctionDef):
                has_bool = (n.name == '__bool__')

        if has_bool:
            self._tree_changed = True
            nonzero = ast.Name(id='__nonzero__', ctx=ast.Store())
            bool_ = ast.Name(id='__bool__', ctx=ast.Load())
            node.body.append(ast.Assign(targets=[nonzero], value=bool_))

        return self.generic_visit(node)  # type: ignore
