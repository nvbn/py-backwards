from typing import Optional, List, Type, Iterable, Union
from typed_ast import ast3 as ast
from .base import BaseTransformer

Node = Union[ast.Try, ast.If, ast.While, ast.For, ast.FunctionDef, ast.Module]
Holder = Union[ast.Expr, ast.Assign]


class YieldFromTransformer(BaseTransformer):
    """Compiles yield from to special while statement."""
    target = (3, 2)
    _name_suffix = 0

    def _get_yield_from_index(self, node: ast.AST,
                              type_: Type[Holder]) -> Optional[int]:
        if hasattr(node, 'body'):  # type: ignore
            for n, child in enumerate(node.body):  # type: ignore
                if isinstance(child, type_) and isinstance(child.value, ast.YieldFrom):
                    return n

        return None

    def _emulate_yield_from(self, targets: Optional[List[ast.Name]],
                            node: ast.YieldFrom) -> Iterable[ast.AST]:
        generator = ast.Name(
            id='_py_backwards_generator_{}'.format(self._name_suffix))
        exception = ast.Name(
            id='_py_backwards_generator_exception_{}'.format(self._name_suffix))

        yield ast.Assign(targets=[generator],
                         value=ast.Call(func=ast.Name(id='iter'),
                                        args=[node.value],
                                        keywords=[]))

        assign_to_targets = [
            ast.If(test=ast.Call(func=ast.Name(id='hasattr'), args=[
                exception, ast.Str(s='value'),
            ], keywords=[]), body=[
                ast.Assign(targets=targets,
                           value=ast.Attribute(
                               value=exception, attr='value')),
            ], orelse=[]),
            ast.Break()] if targets else [ast.Break()]

        yield ast.While(test=ast.NameConstant(value=True), body=[
            ast.Try(body=[
                ast.Expr(value=ast.Yield(value=ast.Call(
                    func=ast.Name(id='next'),
                    args=[generator], keywords=[]))),
            ], handlers=[
                ast.ExceptHandler(
                    type=ast.Name(id='StopIteration'),
                    name=exception.id,
                    body=assign_to_targets),
            ], orelse=[], finalbody=[]),
        ], orelse=[])
        self._name_suffix += 1

    def _handle_assignments(self, node: Node) -> Node:
        while True:
            index = self._get_yield_from_index(node, ast.Assign)
            if index is None:
                return node

            assign = node.body.pop(index)
            for new_node in list(self._emulate_yield_from(assign.targets,  # type: ignore
                                                          assign.value))[::-1]:  # type: ignore
                node.body.insert(index, new_node)  # type: ignore

    def _handle_expressions(self, node: Node) -> Node:
        while True:
            index = self._get_yield_from_index(node, ast.Expr)
            if index is None:
                return node

            assign = node.body.pop(index)
            for new_node in list(self._emulate_yield_from(
                    None, assign.value))[::-1]:  # type: ignore
                node.body.insert(index, new_node)  # type: ignore

    def visit(self, node: ast.AST) -> ast.AST:
        node = self._handle_assignments(node)  # type: ignore
        node = self._handle_expressions(node)  # type: ignore
        return self.generic_visit(node)  # type: ignore
