from inspect import getsource
from typing import Callable, List, Iterable
from typed_ast import ast3 as ast
from ..types import CompilationTarget


class BaseTransformer(ast.NodeTransformer):
    target = None  # type: CompilationTarget
    shim = []  # type: List[Callable]

    def _get_shim(self) -> Iterable[ast.stmt]:
        for shim in self.shim:
            source = getsource(shim)
            yield ast.parse(source).body[0]  # type: ignore

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """Inject special function for merging dicts."""
        shim = list(self._get_shim())
        if shim:
            node.body = shim + node.body

        return self.generic_visit(node)  # type: ignore
