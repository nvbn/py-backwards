from typing import Union, Iterable, List
from typed_ast import ast3 as ast
from .base import BaseNodeTransformer

Splitted = Union[List[ast.expr], ast.Starred]
ListEntry = Union[ast.Call, ast.List]


class StarredUnpackingTransformer(BaseNodeTransformer):
    """Compiles:
        [2, *range(10), 1]
        print(*range(1), *range(3))
    To:
        [2] + list(range(10)) + [1]
        print(*(list(range(1)) + list(range(3))))
        
    """
    target = (3, 4)

    def _has_starred(self, xs: List[ast.expr]) -> bool:
        for x in xs:
            if isinstance(x, ast.Starred):
                return True

        return False

    def _split_by_starred(self, xs: Iterable[ast.expr]) -> List[Splitted]:
        """Split `xs` to separate list by Starred."""
        lists = [[]]  # type: List[Splitted]
        for x in xs:
            if isinstance(x, ast.Starred):
                lists.append(x)
                lists.append([])
            else:
                assert isinstance(lists[-1], list)
                lists[-1].append(x)
        return lists

    def _prepare_lists(self, xs: List[Splitted]) -> Iterable[ListEntry]:
        """Wrap starred in list call and list elts to just List."""
        for x in xs:
            if isinstance(x, ast.Starred):
                yield ast.Call(
                    func=ast.Name(id='list'),
                    args=[x.value],
                    keywords=[])
            elif x:
                yield ast.List(elts=x)

    def _merge_lists(self, xs: List[ListEntry]) -> Union[ast.BinOp, ListEntry]:
        """Merge lists by summing them."""
        if len(xs) == 1:
            return xs[0]

        result = ast.BinOp(left=xs[0], right=xs[1], op=ast.Add())
        for x in xs[2:]:
            result = ast.BinOp(left=result, right=x, op=ast.Add())
        return result

    def _to_sum_of_lists(self, xs: List[ast.expr]) -> Union[ast.BinOp, ListEntry]:
        """Convert list of arguments / list to sum of lists."""
        splitted = self._split_by_starred(xs)
        prepared = list(self._prepare_lists(splitted))
        return self._merge_lists(prepared)

    def visit_List(self, node: ast.List) -> ast.List:
        if not self._has_starred(node.elts):
            return self.generic_visit(node)  # type: ignore

        self._tree_changed = True

        return self.generic_visit(self._to_sum_of_lists(node.elts))  # type: ignore

    def visit_Call(self, node: ast.Call) -> ast.Call:
        if not self._has_starred(node.args):
            return self.generic_visit(self.generic_visit(node))  # type: ignore

        self._tree_changed = True

        args = self._to_sum_of_lists(node.args)
        node.args = [ast.Starred(value=args)]
        return self.generic_visit(node)  # type: ignore
