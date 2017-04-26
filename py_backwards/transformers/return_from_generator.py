from typing import List, Tuple, Any
from typed_ast import ast3 as ast
from .base import BaseTransformer


class ReturnFromGeneratorTransformer(BaseTransformer):
    """Compiles return in generators like:
        def fn():
            yield 1
            return 5
    To:
        def fn():
            yield 1
            exc = StopIteration()
            exc.value = 5
            raise exc
    """
    target = (3, 2)
    _name_suffix = 0

    def _find_generator_returns(self, node: ast.FunctionDef) \
            -> List[Tuple[ast.stmt, ast.Return]]:
        """Using bfs find all `return` statements in function."""
        to_check = [(node, x) for x in node.body]  # type: ignore
        returns = []
        has_yield = False
        while to_check:
            parent, current = to_check.pop()

            if isinstance(current, ast.FunctionDef):
                continue
            elif hasattr(current, 'value'):
                to_check.append((current, current.value))  # type: ignore
            elif hasattr(current, 'body'):
                to_check.extend([(parent, x) for x in current.body])  # type: ignore

            if isinstance(current, ast.Yield) or isinstance(current, ast.YieldFrom):
                has_yield = True

            if isinstance(current, ast.Return) and current.value is not None:
                returns.append((parent, current))

        if has_yield:
            return returns  # type: ignore
        else:
            return []

    def _replace_return(self, parent: Any, return_: ast.Return) -> None:
        """Replace return with exception raising."""
        index = parent.body.index(return_)
        parent.body.pop(index)

        exception = ast.Name(id='_py_backwards_generator_return_{}'.format(
            self._name_suffix))

        raise_exception = ast.Raise(exc=exception, cause=None)
        parent.body.insert(index, raise_exception)

        set_value = ast.Assign(targets=[
            ast.Attribute(value=exception, attr='value'),
        ], value=return_.value)
        parent.body.insert(index, set_value)

        assign = ast.Assign(targets=[exception],
                            value=ast.Call(func=ast.Name(id='StopIteration'),
                                           args=[],
                                           keywords=[]))
        parent.body.insert(index, assign)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        generator_returns = self._find_generator_returns(node)
        for parent, return_ in generator_returns:
            self._replace_return(parent, return_)

        return self.generic_visit(node)  # type: ignore
