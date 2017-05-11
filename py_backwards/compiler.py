from copy import deepcopy
from time import time
from traceback import format_exc
from typing import List, Tuple, Optional
from typed_ast import ast3 as ast
from astunparse import unparse, dump
from autopep8 import fix_code
from .files import get_input_output_paths, InputOutput
from .transformers import transformers
from .types import CompilationTarget, CompilationResult
from .exceptions import CompilationError, TransformationError
from .utils.helpers import debug


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

    return fix_code(code), dependencies


def _compile_file(paths: InputOutput, target: CompilationTarget) -> List[str]:
    """Compiles a single file."""
    with paths.input.open() as f:
        code = f.read()

    try:
        transformed, dependencies = _transform(paths.input.as_posix(),
                                               code, target)
    except SyntaxError as e:
        raise CompilationError(paths.input.as_posix(),
                               code, e.lineno, e.offset)

    try:
        paths.output.parent.mkdir(parents=True)
    except FileExistsError:
        pass

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
