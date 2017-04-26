from time import time
from .files import get_input_output_paths, InputOutput
from .transformers import transform
from .types import CompilationTarget, CompilationResult
from .exceptions import CompilationError


def _compile_file(paths: InputOutput, target: CompilationTarget) -> None:
    """Compiles a single file."""
    with paths.input.open() as f:
        code = f.read()

    try:
        transformed = transform(paths.input.as_posix(),
                                code,
                                target)
    except SyntaxError as e:
        raise CompilationError(paths.input.as_posix(),
                               code, e.lineno, e.offset)

    try:
        paths.output.parent.mkdir(parents=True)
    except FileExistsError:
        pass

    with paths.output.open('w') as f:
        f.write(transformed)


def compile_files(input_: str, output: str,
                  target: CompilationTarget) -> CompilationResult:
    """Compiles all files from input_ to output."""
    start = time()
    count = 0
    for paths in get_input_output_paths(input_, output):
        count += 1
        _compile_file(paths, target)
    return CompilationResult(count, time() - start, target)
