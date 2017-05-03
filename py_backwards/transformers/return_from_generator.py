from typing import List, Tuple, Any
from typed_ast import ast3 as ast
from ..utils.snippet import snippet, let
from .base import BaseNodeTransformer


@snippet
def return_from_generator(return_value):
    let(exc)
    exc = StopIteration()
    exc.value = return_value
    raise exc


class ReturnFromGeneratorTransformer(BaseNodeTransformer):
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
            elif hasattr(current, 'body') and isinstance(current.body, list):  # type: ignore
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

        for line in return_from_generator.get_body(return_value=return_.value)[::-1]:
            parent.body.insert(index, line)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        generator_returns = self._find_generator_returns(node)

        if generator_returns:
            self._tree_changed = True

        for parent, return_ in generator_returns:
            self._replace_return(parent, return_)

        return self.generic_visit(node)  # type: ignore
