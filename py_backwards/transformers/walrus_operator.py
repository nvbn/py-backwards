import functools
import sys
from ..const import TARGET_ALL
from ..exceptions import NodeNotFound
from ..types import TransformationResult
from ..utils.helpers import VariablesGenerator, warn
from ..utils.tree import find, get_node_position, get_parent, insert_at
from ..utils.snippet import snippet
from .. import ast
from .base import BaseNodeTransformer
from typing import Optional

PY38 = sys.version_info >= (3, 8)

if sys.version_info < (3, 8):
    class NamedExpr(ast.AST):
        pass

    class Constant(ast.AST):
        pass
else:
    NamedExpr = ast.NamedExpr
    Constant = ast.Constant

# The standard walrus operator transformer, this one can only transform more
#   basic usage of walrus operators in certain if and while statements.
class WalrusTransformer(BaseNodeTransformer):
    """Compiles:
        if (x := 1 // 2):
            print(0)
        elif (x := 5) and x > 2:
            print(x)
        else:
            print(2)

        while buf := sock.recv(4096):
            print(buf)
    To
        x = 1 // 2
        if x:
            print(0)
        else:
            x = 5
            if x > 2:
                print(1)
            else:
                print(2)

        while True:
            buf = sock.recv(4096)
            if not buf:
                break
            print(buf)

    """
    # Although the walrus operator gets patched into astunparse, autopep8
    #   doesn't (yet) know how to handle walrus operators correctly, so this
    #   has to TARGET_ALL.
    target = TARGET_ALL

    def _get_walruses(self, nodes):
        """
        Recursively search for walruses that are most likely safe to be moved
        outside the current statement.
        """
        if not isinstance(nodes, (tuple, list, map)):
            nodes = (nodes,)

        for node in nodes:
            if isinstance(node, NamedExpr):
                yield node

            if isinstance(node, ast.Compare):
                yield from self._get_walruses(node.left)
                yield from self._get_walruses(node.comparators)
            elif isinstance(node, ast.BoolOp):
                yield from self._get_walruses(node.values[0])
            elif isinstance(node, ast.UnaryOp):
                yield from self._get_walruses(node.operand)
            elif isinstance(node, ast.Call):
                yield from self._get_walruses(node.args)
                yield from self._get_walruses(map(lambda arg : arg.value,
                                                  node.keywords))

    def _has_walrus(self, nodes) -> bool:
        """
        Returns True if self._get_walruses(nodes) is not empty, otherwise
        False.
        """
        try:
            next(iter(self._get_walruses(nodes)))
            return True
        except StopIteration:
            return False

    def _invert_expr(self, node: ast.AST) -> ast.AST:
        """
        Prepends an AST expression with 'not' or removes an existing 'not'.
        """
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return node.operand

        return ast.UnaryOp(op=ast.Not(), operand=node)

    def visit_While(self, node: ast.While) -> ast.While:
        """
        Compiles:
            while data := sock.recv(8192):
                print(data)
        To
            while True:
                if not (data := sock.recv(8192)):
                    break
                print(data)
        """

        # If the condition contains a walrus operator, move the test into an
        #   if statement and let the if handler in transform() deal with it.
        if not node.orelse and self._has_walrus(node.test):
            self._tree_changed = True
            # Remove redundant not statements.
            n = self._invert_expr(node.test)
            node.body.insert(0, ast.If(test=n, body=[ast.Break()], orelse=[]))
            node.test = ast.NameConstant(value=True)

        return self.generic_visit(node) # type: ignore

    def _has_walrus_any(self, node) -> bool:
        """
        Checks if any walrus operators are in node without any sanity checks.
        """
        try:
            next(iter(find(node, NamedExpr)))
            return True
        except StopIteration:
            return False

    def visit_If(self, node: ast.If) -> Optional[ast.AST]:
        """
        Compiles:
            if test1 and (test2 := do_something()):
                pass

            if test1 and test2:
                pass
        To
            if test1:
                if test2 := do_something():
                    pass

            if test1 and test2:
                pass
        """
        if node.orelse or not isinstance(node.test, ast.BoolOp) or \
                not isinstance(node.test.op, ast.And):
            return self.generic_visit(node)

        # Split and-s into multiple if statements if they contain walruses.
        for i, value in enumerate(node.test.values):
            if not i or not self._has_walrus_any(value):
                continue

            # Split the if statement
            self._tree_changed = True

            new_values = node.test.values[i:]
            if i > 1:
                node.test.values = node.test.values[:i]
            else:
                node.test = node.test.values[0]

            if len(new_values) > 1:
                test = ast.BoolOp(op=ast.And(), values=new_values) # type: ast.AST
            else:
                test = new_values[0]

            new_if = ast.If(test=test, body=node.body, orelse=[])
            node.body = [new_if]

            break

        return self.generic_visit(node)

    # This fixes standalone walrus operators (that shouldn't exist in the first
    #   place).
    def visit_Expr(self, node: ast.Expr) -> Optional[ast.AST]:
        """
        Compiles:
            (a := 1)
        To
            a = 1
        """
        if isinstance(node.value, NamedExpr):
            self._tree_changed = True
            new_node = ast.Assign(targets=[node.value.target],
                                  value=node.value.value)
            return self.generic_visit(new_node)

        return self.generic_visit(node)

    def _replace_walruses(self, test: ast.AST):
        """
        Replaces walrus operators in the current if statement and yields Assign
        expressions to add before the if statement.
        """
        for walrus in self._get_walruses(test):
            target = walrus.target
            if isinstance(target, ast.Name):
                target = ast.Name(id=target.id, ctx=ast.Load())
            parent = get_parent(self._tree, walrus)

            if isinstance(parent, ast.keyword):
                parent = get_parent(self._tree, parent)

            if isinstance(parent, ast.Compare):
                if parent.left is walrus:
                    parent.left = target
                else:
                    comps = parent.comparators
                    comps[comps.index(walrus)] = target
            elif isinstance(parent, ast.BoolOp):
                parent.values[0] = target
            elif isinstance(parent, ast.UnaryOp):
                parent.operand = target
            elif isinstance(parent, ast.If):
                parent.test = target
            elif isinstance(parent, ast.Call):
                if walrus in parent.args:
                    parent.args[parent.args.index(walrus)] = walrus.target
                else:
                    for kw in parent.keywords:
                        if kw.value is walrus:
                            kw.value = target
                            break
                    else:
                        raise AssertionError('Failed to find walrus in Call.')
            else:
                raise NotImplementedError(parent)

            yield ast.Assign(targets=[walrus.target], value=walrus.value)


    @classmethod
    def transform(cls, tree: ast.AST) -> TransformationResult:
        self = cls(tree)
        self.visit(tree)

        # Do if statement transformations here so values can be set outside of
        #   the statement, if this is done in visit_If weird things happen.
        for node in find(tree, ast.If):
            try:
                position = get_node_position(tree, node)
            except (NodeNotFound, ValueError):
                warn('If statement outside of body')
                continue

            for i, assign in enumerate(self._replace_walruses(node.test)):
                self._tree_changed = True
                position.holder.insert(position.index + i, assign)

        return TransformationResult(tree, self._tree_changed, [])

# A CPython-only fallback. This uses an undocumented feature.
@snippet
def walrus_snippet(ctypes_):
    let(ctypes)
    let(getframe)
    import ctypes_ as ctypes
    from sys import _getframe as getframe

    def _py_backwards_walrus(name, value):
        frame = getframe(1)
        frame.f_locals[name] = value
        ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame),
                                              ctypes.c_int(0))
        del frame
        return value

# The fallback walrus operator, this can handle more walrus operators,
#   however only works on CPython and if the variable used has been defined
#   in the same scope.
class FallbackWalrusTransformer(BaseNodeTransformer):
    """Compiles:
        def test(e):
            l = None
            if (l := len(e)) > 50:
                raise TypeError(f'Object too long ({l} characters).')
    To
        def test(e):
            l = None
            if _py_backwards_walrus('l', len(e)) > 50:
                raise TypeError(f'Object too long ({l} characters).')

    """
    target = TARGET_ALL

    # Convert standalone NamedExprs
    def visit_NamedExpr(self, node: NamedExpr) -> ast.Call:
        if not self._tree_changed:
            self._tree_changed = True
            warn('The fallback named expression transformer has been used, '
                 'the resulting code will only work in CPython (if at all).')

        target = node.target
        if not isinstance(target, ast.Name):
            raise NotImplementedError

        call = ast.Call(func=ast.Name(id='_py_backwards_walrus',
                                      ctx=ast.Store()),
                        args=[Constant(value=target.id), node.value],
                        keywords=[])

        return self.generic_visit(call)  # type: ignore

    @classmethod
    def transform(cls, tree: ast.AST) -> TransformationResult:
        res = super().transform(tree)
        if res.tree_changed and hasattr(tree, 'body'):
            insert_at(0, tree, walrus_snippet.get_body(ctypes_='ctypes'))
        return res
