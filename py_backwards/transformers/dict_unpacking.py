from typed_ast import ast3 as ast
from .base import BaseTransformer


def _py_backwards_merge_dicts(dicts):
    result = {}
    for dict_ in dicts:
        result.update(dict_)
    return result


class DictUnpackingTransformer(BaseTransformer):
    target = (3, 4)
    shim = [_py_backwards_merge_dicts]

    def _split_by_None(self, pairs):
        result = [[]]
        for key, value in pairs:
            if key is None:
                result.append(value)
                result.append([])
            else:
                result[-1].append((key, value))

        return result

    def _prepare_splitted(self, splitted):
        for group in splitted:
            if not isinstance(group, list):
                yield ast.Call(
                    func=ast.Name(id='dict', ctx=ast.Load()),
                    args=[group],
                    keywords=[])
            elif group:
                yield ast.Dict(keys=[key for key, _ in group],
                               values=[value for _, value in group])

    def _merge_dicts(self, splitted):
        return ast.Call(
            func=ast.Name(id='_py_backwards_merge_dicts'),
            args=[ast.List(elts=splitted)],
            keywords=[])

    def visit_Dict(self, node):
        if None not in node.keys:
            return self.generic_visit(node)

        pairs = zip(node.keys, node.values)
        splitted = self._split_by_None(pairs)
        prepared = self._prepare_splitted(splitted)
        return self._merge_dicts(prepared)
