import sys
from typing import Union
from ..utils.tree import insert_at
from ..utils.snippet import snippet
from .. import ast
from .base import BaseNodeTransformer

if sys.version_info >= (3, 4):
    MatMult, NameConstant = ast.MatMult, ast.NameConstant
else:
    MatMult = None
    def NameConstant(obj):
        return ast.Name(repr(obj))

@snippet
def _matmul():
    def _py_backwards_matmul(left, right):
        """ Same as a @ b. """

        res = NotImplemented
        lt = type(left)
        rt = type(right)

        if hasattr(lt, '__matmul__'):
            res = lt.__matmul__(left, right)
        if res is NotImplemented and hasattr(rt, '__rmatmul__'):
            res = rt.__rmatmul__(right, left)

        if res is NotImplemented:
            raise TypeError('unsupported operand type(s) for @: '
                + repr(lt.__name__) + ' and ' + repr(rt.__name__))
        return res

    def _py_backwards_imatmul(left, right):
        """ Same as a @= b. """
        lt = type(left)
        if hasattr(lt, '__imatmul__'):
            res = lt.__imatmul__(left, right)
            if res is not NotImplemented:
                return res
        try:
            return _py_backwards_matmul(left, right)
        except TypeError as e:
            msg = str(e)
        raise TypeError(msg.replace('@', '@=', 1))

    # Use the existing matmul implementation if available. This should also
    #   delete duplicate _py_backwards_matmul-s across multiple modules.
    let(op)
    import operator as op
    try:
        _py_backwards_matmul = op.matmul
        _py_backwards_imatmul = op.imatmul
    except AttributeError:
        op.matmul = _py_backwards_matmul
        op.imatmul = _py_backwards_imatmul
    del op

class MatMultTransformer(BaseNodeTransformer):
    """Compiles:
        print(a @ b)
        a @= b
    To
        print(_py_backwards_matmul(a, b))
        a = _py_backwards_imatmul(a, b)

    """
    target = (3, 4)

    def visit_Module(self, node: ast.Module) -> ast.Module:
        insert_at(0, node, _matmul.get_body())
        return self.generic_visit(node)  # type: ignore

    def visit_BinOp(self, node: ast.BinOp) -> Union[ast.BinOp, ast.Call]:
        if not isinstance(node.op, MatMult):
            return self.generic_visit(node)  # type: ignore

        self._tree_changed = True
        call = ast.Call(func=ast.Name(id='_py_backwards_matmul'),
            args=[node.left, node.right], keywords=[])
        return self.generic_visit(call)  # type: ignore

    def visit_AugAssign(self, node: ast.AugAssign) \
            -> Union[ast.AugAssign, ast.Assign]:
        if not isinstance(node.op, MatMult):
            return self.generic_visit(node)  # type: ignore

        self._tree_changed = True
        call = ast.Call(func=ast.Name(id='_py_backwards_imatmul'),
            args=[node.target, node.value], keywords=[])

        assign = ast.Assign(targets=[node.target], value=call)
        return self.generic_visit(assign)  # type: ignore
