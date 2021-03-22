from .. import ast
from ..const import TARGET_ALL
from .base import BaseNodeTransformer
from typing import List, Union

# Because astunparse does not handle format strings nicely, this transformer
#   has to target all Python versions (even 3.6 and 3.7).

class FormattedValuesTransformer(BaseNodeTransformer):
    """Compiles:
        f"hello {x}"
    To
        'hello {}'.format(x)

    """
    target = TARGET_ALL

    def _parse_formatted_value(self, i: ast.FormattedValue, keywords: list) \
            -> str:
        """
        Parse a FormattedValue and return a format string to add to a format()
        call. The "keywords" argument is used to add keyword arguments for
        nested format strings.
        """
        res = '{'

        if i.conversion and i.conversion > 0:
            res += '!' + chr(i.conversion)

        if i.format_spec:
            spec = i.format_spec

            # A single ast.Str can just be returned as-is.
            if not isinstance(spec, ast.JoinedStr):
                assert isinstance(spec, ast.Str)
                res += ':' + spec.s
            elif len(spec.values) == 1 and isinstance(spec.values[0], ast.Str):
                res += ':' + spec.values[0].s
            else:
                # For more complicated format strings, add the JoinedStr to the
                #   keyword arguments list.
                kwarg = 'x{:x}'.format(len(keywords))
                keywords.append(ast.keyword(arg=kwarg, value=spec))
                res += ':{' + kwarg + '}'

        return res + '}'

    def visit_FormattedValue(self, node: ast.FormattedValue) -> ast.Call:
        self._tree_changed = True

        keywords = [] # type: List[ast.keyword]
        template = self._parse_formatted_value(node, keywords)

        format_call = ast.Call(func=ast.Attribute(value=ast.Str(s=template),
                                                  attr='format'),
                               args=[node.value], keywords=keywords)
        return self.generic_visit(format_call)  # type: ignore

    def visit_JoinedStr(self, node: ast.JoinedStr) -> Union[ast.Call, ast.Str]:
        self._tree_changed = True

        fs = []
        args = []
        keywords = [] # type: List[ast.keyword]
        for i in node.values:
            if isinstance(i, ast.Str):
                fs.append(i.s.replace('{', '{{').replace('}', '}}'))
            elif isinstance(i, ast.FormattedValue):
                fs.append(self._parse_formatted_value(i, keywords))
                args.append(i.value)
            else:
                raise TypeError(i)

        value = ast.Str(s=''.join(fs))
        if not args:
            return value

        format_call = ast.Call(func=ast.Attribute(value=value,
                                                  attr='format'),
                               args=args, keywords=keywords)
        return self.generic_visit(format_call)  # type: ignore
