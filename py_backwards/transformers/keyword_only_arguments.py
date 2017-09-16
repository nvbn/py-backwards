from typed_ast import ast3 as ast
from .base import BaseNodeTransformer


class KeywordOnlyArgumentsTransformer(BaseNodeTransformer):
    """Compiles:
        def fn(x, *, a=None):
            pass
    To:
        def fn(x, a=None):
            pass

    """
    target = (2, 7)

    def visit_arguments(self, node):
        if node.kwonlyargs:
            self._tree_changed = True

            if node.defaults:
                required_args = node.args[:-len(node.defaults)]
                optional_args = node.args[-len(node.defaults):]
            else:
                required_args = node.args
                optional_args = []

            for kwarg, default in zip(node.kwonlyargs, node.kw_defaults):
                if default is None:
                    required_args.append(kwarg)
                else:
                    optional_args.append(kwarg)
                    node.defaults.append(default)

            node.args = required_args + optional_args
            node.kwonlyargs = []
            node.kw_defaults = []

        return self.generic_visit(node)
