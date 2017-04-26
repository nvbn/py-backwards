from collections import namedtuple
from time import time
from .files import get_input_output_paths
from .transformers import transform


class CompilationError(Exception):
    """Raises when compilation failed because fo syntax error."""

    def __init__(self, filename, code, lineno, offset):
        self.filename = filename
        self.code = code
        self.lineno = lineno
        self.offset = offset


CompilationResult = namedtuple('CompilationResult', ('files',
                                                     'time',
                                                     'target'))


def _compile_file(paths, target):
    """Compiles a single file."""
    with paths.input.open() as f:
        code = f.read()

    try:
        transformed = transform(paths.input.as_posix(),
                                code,
                                target)
    except SyntaxError as e:
        raise CompilationError(e.filename, code, e.lineno, e.offset)

    try:
        paths.output.parent.mkdir(parents=True)
    except FileExistsError:
        pass

    with paths.output.open('w') as f:
        f.write(transformed)


def compile_files(input_, output, target):
    """Compiles all files from input_ to output."""
    start = time()
    count = 0
    for paths in get_input_output_paths(input_, output):
        count += 1
        _compile_file(paths, target)
    return CompilationResult(count, time() - start, target)
