import sys
from ..utils.helpers import VariablesGenerator
from ..utils.snippet import snippet
from ..utils.tree import get_node_position, find, insert_at
from .. import ast
from .base import BaseNodeTransformer
from typing import Callable, Dict, List, Optional, Set, Union

class _ScopeTransformer(ast.NodeTransformer):
    """
    Renames objects so they use scope dictionaries, this is called by
    _RawTransformer.transform() after running its own transformations.
    """

    def __init__(self, scope: Dict[str, str], tree: ast.AST) -> None:
        self.scope = scope
        self.tree = tree

    def visit_Name(self, node: ast.Name) -> Union[ast.Name, ast.Subscript]:
        if node.id not in self.scope:
            return node

        value = ast.Name(id=self.scope[node.id], ctx=ast.Load())

        # Python 2's unicode strings typically use either 2 or 4 bytes, use
        # 8-bit strings (bytes in Python 3) if possible.
        try:
            s = ast.Bytes(s=node.id.encode('ascii')) # type: ast.AST
        except UnicodeEncodeError:
            s = ast.Str(s=node.id)

        subscript = ast.Subscript(value=value, slice=ast.Index(value=s),
                                  ctx=getattr(node, 'ctx', None) or ast.Load())
        return subscript

    def _assign_later(self, node: ast.AST, name: str) -> str:
        pos = get_node_position(self.tree, node)
        temp_name = VariablesGenerator.generate('temp_' + name)
        assign = ast.Assign(targets=[ast.Name(id=name, ctx=ast.Store())],
                            value=ast.Name(id=temp_name, ctx=ast.Load()))
        pos.holder.insert(pos.index + 1, assign)
        delete = ast.Delete(targets=[ast.Name(id=temp_name,
                                              ctx=ast.Del())])
        pos.holder.insert(pos.index + 2, delete)

        return temp_name

    def visit_FunctionDef(self, node: Union[ast.FunctionDef, ast.ClassDef]) \
            -> Union[ast.FunctionDef, ast.ClassDef]:
        if node.name in self.scope:
            node.name = self._assign_later(node, node.name)

        # Don't call generic_visit() here.
        return node

    visit_ClassDef = visit_FunctionDef

    # Used in import and import from statements.
    def visit_alias(self, node: ast.alias) -> ast.alias:
        name = node.asname or node.name
        if name and name in self.scope:
            node.asname = self._assign_later(node, name)

        return self.generic_visit(node) # type: ignore

class _RawTransformer(ast.NodeTransformer):
    def __init__(self, node: Union[ast.FunctionDef, ast.ClassDef],
            callbacks: List[Callable], *, parent_name: Optional[str] = None,
            parent_scope: Optional[Dict[str, str]] = None) -> None:
        self.parent_name = parent_name
        self.name = None # type: Optional[str]
        self.node = node
        self.is_class = isinstance(node, ast.ClassDef) # type: bool
        self.tree_changed = False # type: bool
        self._callbacks = callbacks
        if parent_scope is None:
            parent_scope = {}
        self.parent_scope = parent_scope # type: Dict[str, str]
        self.scope = {} # type: Dict[str, str]

    @classmethod
    def transform(cls, node: Union[ast.FunctionDef, ast.ClassDef],
            parent: Union[ast.FunctionDef, ast.ClassDef],
            callbacks: List[Callable], *, parent_name: Optional[str] = None,
            parent_scope: Optional[Dict[str, str]] = None) -> '_RawTransformer':
        self = cls(node, callbacks, parent_name=parent_name,
                   parent_scope=parent_scope)
        for n in node.body:
            self.visit(n)

        if not self.tree_changed:
            return self

        scopetransformer = _ScopeTransformer(self.scope, node)
        for n in node.body:
            scopetransformer.visit(n)

        if not self.parent_name or isinstance(parent, ast.ClassDef):
            return self

        # Add the scope variable
        if not parent_name:
            name = ast.Name(id=self.parent_name, ctx=ast.Store())
            assign = ast.Assign(targets=[name],
                                value=ast.Dict(keys=[], values=[]))

            i = 0
            if parent.body and isinstance(parent.body[0], ast.Expr) and \
                    isinstance(parent.body[0].value, ast.Str):
                i = 1
            self._callbacks.append(lambda : parent.body.insert(i, assign))

        return self

    def visit_FunctionDef(self, node: Union[ast.FunctionDef, ast.ClassDef]) \
            -> Union[ast.FunctionDef, ast.ClassDef]:
        # Classes are different.
        if self.is_class:
            name, scope = self.parent_name, self.parent_scope
        else:
            name, scope = self.name, self.scope

        transformer = self.transform(node, self.node, self._callbacks,
                                     parent_name=name, parent_scope=scope)
        if transformer.tree_changed:
            self.tree_changed = True
            self.name = transformer.parent_name

        # Don't call generic_visit(), that would iterate over the nodes inside
        #   the function.
        return node

    visit_ClassDef = visit_FunctionDef

    def visit_Nonlocal(self, node: ast.Nonlocal) -> ast.Nonlocal:
        self.tree_changed = True
        if self.parent_name is None:
            self.parent_name = VariablesGenerator.generate('scope')

        for name in node.names:
            if name in self.parent_scope:
                scope = self.parent_scope[name]
            else:
                scope = self.parent_name
                self.parent_scope[name] = scope
            self.scope[name] = scope

        position = get_node_position(self.node, node)
        self._callbacks.append(lambda : position.holder.remove(node))

        return node

class NonlocalStatementTransformer(BaseNodeTransformer):
    """Compiles:
        def outer():
            x = 1
            def inner():
                nonlocal x
                x = 2
            inner()
            print(x)
    To
        def outer():
            _py_backwards_scope_0 = {}
            _py_backwards_scope_0['x'] = 1
            def inner():
                _py_backwards_scope_0['x'] = 2
            inner()
            print(_py_backwards_scope_0['x'])

    """
    target = (2, 7)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        callbacks = [] # type: List[Callable]
        transformer = _RawTransformer.transform(node, node, callbacks)
        if transformer.tree_changed:
            self._tree_changed = True
        for callback in reversed(callbacks):
            callback()
        return node  # type: ignore

    def visit_Nonlocal(self, node: ast.Nonlocal):
        exc = SyntaxError('nonlocal outside function')
        exc.ast_node = node # type: ignore
        raise exc
