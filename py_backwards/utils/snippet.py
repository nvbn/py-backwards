from inspect import getsource
from typing import Callable, Any, List, Dict, Iterable, Union
from typed_ast import ast3 as ast
from .tree import find, get_non_exp_parent_and_index
from .helpers import eager


Variable = Union[ast.AST, str]


@eager
def find_variables(tree: ast.AST) -> Iterable[str]:
    """Finds variables and remove `let` calls."""
    for node in find(tree, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == 'let':
            parent, index = get_non_exp_parent_and_index(tree, node)
            parent.body.pop(index)
            yield node.args[0].id


class VariablesGenerator:
    _counter = 0

    @classmethod
    def generate(cls, variable: str) -> str:
        try:
            return '_py_backwards_{}_{}'.format(variable, cls._counter)
        finally:
            cls._counter += 1


class VariablesReplacer(ast.NodeTransformer):
    """Replaces declared variables with unique names."""

    def __init__(self, variables: Dict[str, str]) -> None:
        self._variables = variables

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id in self._variables:
            if isinstance(self._variables[node.id], str):
                node.id = self._variables[node.id]
            else:
                node = self._variables[node.id]

        return self.generic_visit(node)

    def _replace_field(self, node: ast.AST, field: str) -> None:
        value = getattr(node, field, None)
        if value in self._variables:
            if isinstance(self._variables[value], str):
                setattr(node, field, self._variables[value])

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        self._replace_field(node, 'name')
        return self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> ast.Attribute:
        self._replace_field(node, 'name')
        return self.generic_visit(node)

    def visit_keyword(self, node: ast.keyword) -> ast.keyword:
        self._replace_field(node, 'arg')
        return self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        self._replace_field(node, 'name')
        return self.generic_visit(node)

    def visit_arg(self, node: ast.arg) -> ast.arg:
        self._replace_field(node, 'arg')
        return self.generic_visit(node)

    def _replace_module(self, module: str) -> str:
        def _replace(name):
            if name in self._variables:
                if isinstance(self._variables[name], str):
                    return self._variables[name]

            return name

        return '.'.join(_replace(part) for part in module.split('.'))

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        node.module = self._replace_module(node.module)
        return self.generic_visit(node)

    def visit_alias(self, node: ast.alias) -> ast.alias:
        node.name = self._replace_module(node.name)
        self._replace_field(node, 'asname')
        return self.generic_visit(node)

    @classmethod
    def replace(cls, tree: ast.AST, variables: Dict[str, str]) -> ast.AST:
        """Repalces all variables with unique names."""
        inst = cls(variables)
        inst.visit(tree)
        return tree


def extend_tree(tree: ast.AST, variables: Dict[str, Variable]) -> None:
    for node in find(tree, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == 'extend':
            parent, index = get_non_exp_parent_and_index(tree, node)
            parent.body.pop(index)
            for entry in variables[node.args[0].id][::-1]:
                parent.body.insert(index, entry)


# Public api:

class snippet:
    """Snippet of code."""

    def __init__(self, fn: Callable[[Any], None]) -> None:
        self._fn = fn

    def _get_variables(self, tree: ast.AST,
                       snippet_kwargs: Dict[str, Variable]) -> Dict[str, Variable]:
        names = find_variables(tree)
        variables = {name: VariablesGenerator.generate(name)
                     for name in names}

        for key, val in snippet_kwargs.items():
            if isinstance(val, ast.Name):
                variables[key] = val.id
            else:
                variables[key] = val

        return variables

    def get_body(self, **snippet_kwargs: ast.AST) -> List[ast.AST]:
        """Get AST of snippet body."""
        source = getsource(self._fn)
        tree = ast.parse(source)
        variables = self._get_variables(tree, snippet_kwargs)
        extend_tree(tree, variables)
        VariablesReplacer.replace(tree, variables)
        return tree.body[0].body


def let(var: Any) -> None:
    """Declares unique value in snippet."""


def extend(var: Any) -> None:
    """Extend code."""
