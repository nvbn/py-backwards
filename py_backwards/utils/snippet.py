from typing import Callable, Any, List, Dict, Iterable, Union, TypeVar
from typed_ast import ast3 as ast
from .tree import find, get_non_exp_parent_and_index, replace_at
from .helpers import eager, VariablesGenerator, get_source

Variable = Union[ast.AST, List[ast.AST], str]


@eager
def find_variables(tree: ast.AST) -> Iterable[str]:
    """Finds variables and remove `let` calls."""
    for node in find(tree, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == 'let':
            parent, index = get_non_exp_parent_and_index(tree, node)
            parent.body.pop(index)  # type: ignore
            yield node.args[0].id  # type: ignore


T = TypeVar('T', bound=ast.AST)


class VariablesReplacer(ast.NodeTransformer):
    """Replaces declared variables with unique names."""

    def __init__(self, variables: Dict[str, Variable]) -> None:
        self._variables = variables

    def _replace_field_or_node(self, node: T, field: str, all_types=False) -> T:
        value = getattr(node, field, None)
        if value in self._variables:
            if isinstance(self._variables[value], str):
                setattr(node, field, self._variables[value])
            elif all_types or isinstance(self._variables[value], type(node)):
                node = self._variables[value]  # type: ignore

        return node

    def visit_Name(self, node: ast.Name) -> ast.Name:
        node = self._replace_field_or_node(node, 'id', True)
        return self.generic_visit(node)  # type: ignore

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        node = self._replace_field_or_node(node, 'name')
        return self.generic_visit(node)  # type: ignore

    def visit_Attribute(self, node: ast.Attribute) -> ast.Attribute:
        node = self._replace_field_or_node(node, 'name')
        return self.generic_visit(node)  # type: ignore

    def visit_keyword(self, node: ast.keyword) -> ast.keyword:
        node = self._replace_field_or_node(node, 'arg')
        return self.generic_visit(node)  # type: ignore

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        node = self._replace_field_or_node(node, 'name')
        return self.generic_visit(node)  # type: ignore

    def visit_arg(self, node: ast.arg) -> ast.arg:
        node = self._replace_field_or_node(node, 'arg')
        return self.generic_visit(node)  # type: ignore

    def _replace_module(self, module: str) -> str:
        def _replace(name):
            if name in self._variables:
                if isinstance(self._variables[name], str):
                    return self._variables[name]

            return name

        return '.'.join(_replace(part) for part in module.split('.'))

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        node.module = self._replace_module(node.module)
        return self.generic_visit(node)  # type: ignore

    def visit_alias(self, node: ast.alias) -> ast.alias:
        node.name = self._replace_module(node.name)
        node = self._replace_field_or_node(node, 'asname')
        return self.generic_visit(node)  # type: ignore

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> ast.ExceptHandler:
        node = self._replace_field_or_node(node, 'name')
        return self.generic_visit(node)  # type: ignore

    @classmethod
    def replace(cls, tree: T, variables: Dict[str, Variable]) -> T:
        """Replaces all variables with unique names."""
        inst = cls(variables)
        inst.visit(tree)
        return tree


def extend_tree(tree: ast.AST, variables: Dict[str, Variable]) -> None:
    for node in find(tree, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == 'extend':
            parent, index = get_non_exp_parent_and_index(tree, node)
            replace_at(index, parent, variables[node.args[0].id])  # type: ignore


# Public api:

class snippet:
    """Snippet of code."""

    def __init__(self, fn: Callable[..., None]) -> None:
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
                variables[key] = val  # type: ignore

        return variables  # type: ignore

    def get_body(self, **snippet_kwargs: Variable) -> List[ast.AST]:
        """Get AST of snippet body with replaced variables."""
        source = get_source(self._fn)
        tree = ast.parse(source)
        variables = self._get_variables(tree, snippet_kwargs)
        extend_tree(tree, variables)
        VariablesReplacer.replace(tree, variables)
        return tree.body[0].body  # type: ignore


def let(var: Any) -> None:
    """Declares unique value in snippet. Code of snippet like:
    
        let(x)
        x += 1
        y = 1
        
    Will end up like:
        
        _py_backwards_x_0 += 1
        y = 1
    """


def extend(var: Any) -> None:
    """Extends code, so code like:
    
        extend(vars)
        print(x, y)
        
    When vars contains AST of assignments will end up:
    
        x = 1
        x = 2
        print(x, y)
    """
