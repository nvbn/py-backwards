from inspect import getsource
from typed_ast import ast3 as ast


class BaseTransformer(ast.NodeTransformer):
    target = None
    shim = []

    def _get_shim(self):
        for shim in self.shim:
            source = getsource(shim)
            yield ast.parse(source).body[0]

    def visit_Module(self, node):
        """Inject special function for merging dicts."""
        shim = list(self._get_shim())
        if shim:
            node.body = shim + node.body

        return self.generic_visit(node)
