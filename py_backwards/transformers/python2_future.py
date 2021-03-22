from ..utils.snippet import snippet
from .. import ast
from .base import BaseNodeTransformer
from .kwonlyargs import KwOnlyArgTransformer

@snippet
def imports(future):
    from future import absolute_import
    from future import division
    from future import print_function
    from future import unicode_literals

    try:
        input, range, str, bytes, chr = raw_input, xrange, unicode, str, unichr
    except NameError:
        pass
    else:
        from itertools import ifilter as filter, imap as map, izip as zip

        let(i)
        import itertools as i
        i.filterfalse, i.zip_longest = i.ifilterfalse, i.izip_longest
        del i

def _check_name(node, name):
    return isinstance(node, ast.Name) and node.id == name

class Python2FutureTransformer(BaseNodeTransformer):
    """Prepends module with:
        from __future__ import absolute_import
        from __future__ import division
        from __future__ import print_function
        from __future__ import unicode_literals

    Compiles:
        isinstance(obj, int)
    To
        isinstance(obj, (int, long))

    """
    target = (2, 7)

    def visit_Module(self, node: ast.Module) -> ast.Module:
        self._tree_changed = True
        node.body = imports.get_body(future='__future__') + node.body  # type: ignore
        return self.generic_visit(node)  # type: ignore

    def visit_Call(self, node: ast.Call) -> ast.Call:
        if _check_name(node.func, 'isinstance') and len(node.args) == 2 and \
                _check_name(node.args[1], 'int'):
            self._tree_changed = True
            node.args[1] = ast.Tuple([ast.Name(id='int'),
                                      ast.Name(id='long')])

        return self.generic_visit(node)  # type: ignore

@snippet
def py25_imports(future, itertools_):
    from future import absolute_import
    from future import division
    from future import with_statement
    from six import advance_iterator as next

    let(itertools)
    import itertools_ as itertools
    # Based off of
    #   https://docs.python.org/3/library/itertools.html#itertools.zip_longest
    if hasattr(itertools, 'izip_longest'):
        del itertools
    else:
        def zip_longest(*args, fillvalue=None):
            if not args:
                return
            iterators = [iter(i) for i in args]
            active = len(iterators)
            while True:
                values = []
                for idx, it in enumerate(iterators):
                    try:
                        values.append(next(it))
                    except StopIteration:
                        active -= 1
                        if not active: return
                        iterators[idx] = itertools.repeat(fillvalue)
                        values.append(fillvalue)
                yield tuple(values)

        itertools.izip_longest = zip_longest
        del zip_longest

class Python25FutureTransformer(BaseNodeTransformer):
    """Prepends module with:
        from __future__ import absolute_import
        from __future__ import division
        from __future__ import with_statement
        from six import advance_iterator as next
    And removes __future__ imports added by Python2FutureTransformer.

    """
    target = (2, 5)
    dependencies = ['six']

    def visit_Module(self, node: ast.Module) -> ast.Module:
        self._tree_changed = True
        while node.body and isinstance(node.body[0], ast.ImportFrom) and \
                node.body[0].module == '__future__':
            del node.body[0]

        # Make a Module object to pass to KwOnlyArgTransformer
        body = py25_imports.get_body(future='__future__',
                                     itertools_='itertools')
        tree = ast.Module(body=body)
        tree = KwOnlyArgTransformer(tree).visit(tree)

        # Add it to the module
        node.body = tree.body + node.body
        return self.generic_visit(node)  # type: ignore
