from time import time
from traceback import format_exc
from typing import List, Tuple
from typed_ast import ast3 as ast
from typed_astunparse import unparse, dump
from autopep8 import fix_code
from .files import get_input_output_paths, InputOutput
from .transformers import transformers
from .types import CompilationTarget, CompilationResult
from .exceptions import CompilationError, TransformationError


def _transform(path: str, code: str, target: CompilationTarget) -> Tuple[str, List[str]]:
    """Applies all transformation for passed target."""
    dependencies = []  # type: List[str]

    for transformer in transformers:
        tree = ast.parse(code, path)
        if transformer.target < target:
            continue

        try:
            result = transformer.transform(tree)
        except:
            raise TransformationError(path, transformer,
                                      dump(tree), format_exc())

        if not result.tree_changed:
            continue

        dependencies.extend(result.dependencies)

        try:
            code = unparse(tree)
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


def compile_files(input_: str, output: str,
                  target: CompilationTarget) -> CompilationResult:
    """Compiles all files from input_ to output."""
    dependencies = set()
    start = time()
    count = 0
    for paths in get_input_output_paths(input_, output):
        count += 1
        dependencies.update(_compile_file(paths, target))
    return CompilationResult(count, time() - start, target,
                             sorted(dependencies))
