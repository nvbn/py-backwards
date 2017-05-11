from typing import Union, Iterable, Optional, List, Tuple
from typed_ast import ast3 as ast
from ..utils.tree import insert_at
from ..utils.snippet import snippet
from .base import BaseNodeTransformer


@snippet
def merge_dicts():
    def _py_backwards_merge_dicts(dicts):
        result = {}
        for dict_ in dicts:
            result.update(dict_)
        return result


Splitted = List[Union[List[Tuple[ast.expr, ast.expr]], ast.expr]]
Pair = Tuple[Optional[ast.expr], ast.expr]


class DictUnpackingTransformer(BaseNodeTransformer):
    """Compiles:
    
        {1: 1, **dict_a}
        
    To:
    
        _py_backwards_merge_dicts([{1: 1}], dict_a})
    
    """
    target = (3, 4)

    def _split_by_None(self, pairs: Iterable[Pair]) -> Splitted:
        """Splits pairs to lists separated by dict unpacking statements."""
        result = [[]]  # type: Splitted
        for key, value in pairs:
            if key is None:
                result.append(value)
                result.append([])
            else:
                assert isinstance(result[-1], list)
                result[-1].append((key, value))

        return result

    def _prepare_splitted(self, splitted: Splitted) \
            -> Iterable[Union[ast.Call, ast.Dict]]:
        """Wraps splitted in Call or Dict."""
        for group in splitted:
            if not isinstance(group, list):
                yield ast.Call(
                    func=ast.Name(id='dict'),
                    args=[group],
                    keywords=[])
            elif group:
                yield ast.Dict(keys=[key for key, _ in group],
                               values=[value for _, value in group])

    def _merge_dicts(self, xs: Iterable[Union[ast.Call, ast.Dict]]) \
            -> ast.Call:
        """Creates call of function for merging dicts."""
        return ast.Call(
            func=ast.Name(id='_py_backwards_merge_dicts'),
            args=[ast.List(elts=list(xs))],
            keywords=[])

    def visit_Module(self, node: ast.Module) -> ast.Module:
        insert_at(0, node, merge_dicts.get_body())  # type: ignore
        return self.generic_visit(node)  # type: ignore

    def visit_Dict(self, node: ast.Dict) -> Union[ast.Dict, ast.Call]:
        if None not in node.keys:
            return self.generic_visit(node)  # type: ignore

        self._tree_changed = True
        pairs = zip(node.keys, node.values)
        splitted = self._split_by_None(pairs)
        prepared = self._prepare_splitted(splitted)
        return self._merge_dicts(prepared)
