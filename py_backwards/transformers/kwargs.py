from .. import ast
from ..utils.snippet import snippet
from .base import BaseNodeTransformer
from typing import Optional

@snippet
def _kwarg_lambda():
    lambda **k : k

class KwArgTransformer(BaseNodeTransformer):
    """Compiles:
        args = (1, 2, 3, 4)
        test(*args, a=1)
        test2(**kwargs)
    To
        args = (1, 2, 3, 4)
        test(*args, **{b'a': 1})
        test2(**kwargs)

    """
    target = (2, 5)

    def visit_Call(self, node: ast.Call) -> Optional[ast.AST]:
        # This uses bytes literals because in Python 2.5 those are converted to
        # strings.
        if node.args and isinstance(node.args[-1], ast.Starred) \
                and node.keywords:
            self._tree_changed = True
            if any(True for k in node.keywords if k.arg is None):
                if len(node.keywords) == 1:
                    return self.generic_visit(node)

                # TODO: Something less hacky.
                func = _kwarg_lambda.get_body()[0]
                d = ast.Call(func=func, args=[], keywords=list(node.keywords)) # type: ast.AST
            else:
                d = ast.Dict(keys=[ast.Bytes(s=k.arg.encode('utf-8')) for k in
                                   node.keywords if k.arg],
                             values=[k.value for k in node.keywords])

            node.keywords.clear()
            node.keywords.append(ast.keyword(arg=None, value=d))

        return self.generic_visit(node)
