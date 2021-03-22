from copy import deepcopy
from time import time
from traceback import format_exc
from typing import List, Tuple, Optional
try:
    from ast import dump
except ImportError:
    from astunparse import dump
from autopep8 import fix_code
from .files import get_input_output_paths, InputOutput
from .transformers import transformers
from .types import CompilationTarget, CompilationResult
from .exceptions import CompilationError, TransformationError
from .utils.helpers import debug
from . import ast, const, unparse


def _transform(path: str, code: str, target: CompilationTarget) -> Tuple[str, List[str]]:
    """Applies all transformation for passed target."""
    debug(lambda: 'Compiling "{}"'.format(path))
    dependencies = []  # type: List[str]
    tree = ast.parse(code, path)
    debug(lambda: 'Initial ast:\n{}'.format(dump(tree)))

    for transformer in transformers:
        if transformer.target < target:
            debug(lambda: 'Skip transformer "{}"'.format(transformer.__name__))
            continue

        debug(lambda: 'Use transformer "{}"'.format(transformer.__name__))

        working_tree = deepcopy(tree)
        try:
            result = transformer.transform(working_tree)
        except SyntaxError as exc:
            if isinstance(getattr(exc, 'ast_node', None), ast.AST):
                if not getattr(exc.ast_node, 'lineno', None): # type: ignore
                    ast.fix_missing_locations(working_tree)
                exc.lineno = getattr(exc.ast_node, 'lineno', 0) # type: ignore
                exc.offset = getattr(exc.ast_node, 'col_offset', -1) + 1 # type: ignore
            else:
                exc.lineno = exc.lineno or 0
                exc.offset = exc.offset or 0

            raise exc
        except:
            raise TransformationError(path, transformer,
                                      dump(tree), format_exc())

        if not result.tree_changed:
            debug(lambda: 'Tree not changed')
            continue

        tree = working_tree
        debug(lambda: 'Tree changed:\n{}'.format(dump(tree)))
        dependencies.extend(result.dependencies)

        try:
            code = unparse(tree)
            debug(lambda: 'Code changed:\n{}'.format(code))
        except:
            raise TransformationError(path, transformer,
                                      dump(tree), format_exc())

    # Disable E402 (moving imports to the top of the file) as it breaks.
    code = fix_code(code, options={'ignore': ['E226', 'E24', 'W50', 'W690',
                                              'E402']})
    return code, dependencies


def _compile_file(paths: InputOutput, target: CompilationTarget) -> List[str]:
    """Compiles a single file."""
    with paths.input.open() as f:
        code = f.read()

    try:
        transformed, dependencies = _transform(paths.input.as_posix(),
                                               code, target)
    except SyntaxError as e:
        raise CompilationError(paths.input.as_posix(),
                               code, e.lineno, e.offset or 0)

    try:
        paths.output.parent.mkdir(parents=True)
    except FileExistsError:
        pass

    if target <= const.TARGETS['2.7']:
        transformed = '# -*- coding: utf-8 -*-\n{}'.format(transformed)

    with paths.output.open('w') as f:
        f.write(transformed)

    return dependencies


def compile_files(input_: str, output: str, target: CompilationTarget,
                  root: Optional[str] = None) -> CompilationResult:
    """Compiles all files from input_ to output."""
    dependencies = set()
    start = time()
    count = 0
    for paths in get_input_output_paths(input_, output, root):
        count += 1
        dependencies.update(_compile_file(paths, target))
    return CompilationResult(count, time() - start, target,
                             sorted(dependencies))
