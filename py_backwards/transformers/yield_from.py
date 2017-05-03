from typing import Optional, List, Type, Union
from typed_ast import ast3 as ast
from ..utils.tree import insert_at
from ..utils.snippet import snippet, let, extend
from ..utils.helpers import VariablesGenerator
from .base import BaseNodeTransformer

Node = Union[ast.Try, ast.If, ast.While, ast.For, ast.FunctionDef, ast.Module]
Holder = Union[ast.Expr, ast.Assign]


@snippet
def result_assignment(exc, target):
    if hasattr(exc, 'value'):
        target = exc.value


@snippet
def yield_from(generator, exc, assignment):
    let(iterable)
    iterable = iter(generator)
    while True:
        try:
            yield next(iterable)
        except StopIteration as exc:
            extend(assignment)
            break


class YieldFromTransformer(BaseNodeTransformer):
    """Compiles yield from to special while statement."""
    target = (3, 2)

    def _get_yield_from_index(self, node: ast.AST,
                              type_: Type[Holder]) -> Optional[int]:
        if hasattr(node, 'body') and isinstance(node.body, list):  # type: ignore
            for n, child in enumerate(node.body):  # type: ignore
                if isinstance(child, type_) and isinstance(child.value, ast.YieldFrom):
                    return n

        return None

    def _emulate_yield_from(self, target: Optional[ast.AST],
                            node: ast.YieldFrom) -> List[ast.AST]:
        exc = VariablesGenerator.generate('exc')
        if target is not None:
            assignment = result_assignment.get_body(exc=exc, target=target)
        else:
            assignment = []

        return yield_from.get_body(generator=node.value,
                                   assignment=assignment,
                                   exc=exc)

    def _handle_assignments(self, node: Node) -> Node:
        while True:
            index = self._get_yield_from_index(node, ast.Assign)
            if index is None:
                return node

            assign = node.body.pop(index)
            yield_from_ast = self._emulate_yield_from(assign.targets[0],  # type: ignore
                                                      assign.value)  # type: ignore
            insert_at(index, node, yield_from_ast)
            self._tree_changed = True

    def _handle_expressions(self, node: Node) -> Node:
        while True:
            index = self._get_yield_from_index(node, ast.Expr)
            if index is None:
                return node

            exp = node.body.pop(index)
            yield_from_ast = self._emulate_yield_from(None, exp.value)  # type: ignore
            insert_at(index, node, yield_from_ast)
            self._tree_changed = True

    def visit(self, node: ast.AST) -> ast.AST:
        node = self._handle_assignments(node)  # type: ignore
        node = self._handle_expressions(node)  # type: ignore
        return self.generic_visit(node)  # type: ignore
