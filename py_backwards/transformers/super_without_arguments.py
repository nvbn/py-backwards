from typing import Iterable, Optional
from typed_ast import ast3 as ast
from .base import BaseTransformer


class SuperWithoutArgumentsTransformer(BaseTransformer):
    """Compiles:
        super()
    To:
        super(type(self), self)
        super(cls, cls)
            
    """
    target = (2, 7)

    def _find_super_without_arguments(self, node: ast.FunctionDef) \
            -> Iterable[ast.Call]:
        to_check = list(node.body)
        while to_check:
            current = to_check.pop()

            if isinstance(current, ast.FunctionDef):
                continue
            elif (isinstance(current, ast.Call)
                  and isinstance(current.func, ast.Name)  # type: ignore
                  and current.func.id == 'super'):  # type: ignore
                yield current
            elif hasattr(current, 'func'):
                to_check.append(current.func)  # type: ignore
            elif hasattr(current, 'value'):
                to_check.append(current.value)  # type: ignore
            elif hasattr(current, 'body'):
                to_check.extend(current.body)  # type: ignore

    def _get_method_first_argument(self, node: ast.FunctionDef) -> Optional[str]:
        args = list(node.args.args)
        if args and args[0].arg in ('self', 'cls'):
            return args[0].arg
        else:
            return None

    def _set_arguments_to_super(self, call: ast.Call, first_argument: str):
        super_cls = ast.Name(id='cls') if first_argument == 'cls' else ast.Call(
            func=ast.Name(id='type'),
            args=[ast.Name(id=first_argument)],
            keywords=[])
        call.args = [super_cls, ast.Name(id=first_argument)]

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        method_first_argument = self._get_method_first_argument(node)
        if method_first_argument:
            for call in self._find_super_without_arguments(node):
                self._set_arguments_to_super(call, method_first_argument)

        return self.generic_visit(node)  # type: ignore
