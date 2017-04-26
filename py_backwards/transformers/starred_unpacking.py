from .base import BaseTransformer
from typed_ast import ast3 as ast


class StarredUnpackingTransformer(BaseTransformer):
    target = (3, 4)

    def _has_starred(self, xs):
        for x in xs:
            if isinstance(x, ast.Starred):
                return True

        return False

    def _prepare_lists(self, xs):
        """Wrap starred in list call and list elts to just List."""
        for x in xs:
            if isinstance(x, ast.Starred):
                yield ast.Call(
                    func=ast.Name(id='list'),
                    args=[x.value],
                    keywords=[])
            elif x:
                yield ast.List(elts=x)

    def _split_by_starred(self, xs):
        """Split `xs` to separate list by Starred."""
        lists = [[]]
        for x in xs:
            if isinstance(x, ast.Starred):
                lists.append(x)
                lists.append([])
            else:
                lists[-1].append(x)
        return lists

    def _merge_lists(self, xs):
        """Merge lists by summing them."""
        if len(xs) == 1:
            return xs

        result = ast.BinOp(left=xs[0], right=xs[1], op=ast.Add())
        for x in xs[2:]:
            result = ast.BinOp(left=result, right=x, op=ast.Add())
        return result

    def _to_sum_of_lists(self, xs):
        """Convert list of arguments / list to sum of lists."""
        splitted = self._split_by_starred(xs)
        prepared = list(self._prepare_lists(splitted))
        return self._merge_lists(prepared)

    def visit_List(self, node):
        if not self._has_starred(node.elts):
            return self.generic_visit(node)

        return self._to_sum_of_lists(node.elts)

    def visit_Call(self, node):
        if not self._has_starred(node.args):
            return self.generic_visit(node)

        args = self._to_sum_of_lists(node.args)
        node.args = [ast.Starred(value=args)]
        return node
