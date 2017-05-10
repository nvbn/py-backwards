from typing import Iterable
from colorama import Fore, Style
from .exceptions import CompilationError, TransformationError
from .types import CompilationResult
from . import const


def _format_line(line: str, n: int, padding: int) -> str:
    """Format single line of code."""
    return '  {dim}{n}{reset}: {line}'.format(dim=Style.DIM,
                                              n=str(n + 1).zfill(padding),
                                              line=line,
                                              reset=Style.RESET_ALL)


def _get_lines_with_highlighted_error(e: CompilationError) -> Iterable[str]:
    """Format code with highlighted syntax error."""
    error_line = e.lineno - 1
    lines = e.code.split('\n')
    padding = len(str(len(lines)))

    from_line = error_line - const.SYNTAX_ERROR_OFFSET
    if from_line < 0:
        from_line = 0

    if from_line < error_line:
        for n in range(from_line, error_line):
            yield _format_line(lines[n], n, padding)

    yield '  {dim}{n}{reset}: {bright}{line}{reset}'.format(
        dim=Style.DIM,
        n=str(error_line + 1).zfill(padding),
        line=lines[error_line],
        reset=Style.RESET_ALL,
        bright=Style.BRIGHT)
    yield '  {padding}{bright}^{reset}'.format(
        padding=' ' * (padding + e.offset + 1),
        bright=Style.BRIGHT,
        reset=Style.RESET_ALL)

    to_line = error_line + const.SYNTAX_ERROR_OFFSET
    if to_line > len(lines):
        to_line = len(lines)
    for n in range(error_line + 1, to_line):
        yield _format_line(lines[n], n, padding)


def syntax_error(e: CompilationError) -> str:
    lines = _get_lines_with_highlighted_error(e)

    return ('{red}Syntax error in "{e.filename}", '
            'line {e.lineno}, pos {e.offset}:{reset}\n{lines}').format(
        red=Fore.RED,
        e=e,
        reset=Style.RESET_ALL,
        bright=Style.BRIGHT,
        lines='\n'.join(lines))


def transformation_error(e: TransformationError) -> str:
    return ('{red}{bright}Transformation error in "{e.filename}", '
            'transformer "{e.transformer.__name__}" '
            'failed with:{reset}\n{e.traceback}\n'
            '{bright}AST:{reset}\n{e.ast}').format(
        red=Fore.RED,
        e=e,
        reset=Style.RESET_ALL,
        bright=Style.BRIGHT)


def input_doesnt_exists(input_: str) -> str:
    return '{red}Input path "{path}" doesn\'t exists{reset}'.format(
        red=Fore.RED, path=input_, reset=Style.RESET_ALL)


def invalid_output(input_: str, output: str) -> str:
    return ('{red}Invalid output, when input "{input}" is a directory,'
            'output "{output}" should be a directory too{reset}').format(
        red=Fore.RED, input=input_, output=output, reset=Style.RESET_ALL)


def permission_error(output: str) -> str:
    return '{red}Permission denied to "{output}"{reset}'.format(
        red=Fore.RED, output=output, reset=Style.RESET_ALL)


def compilation_result(result: CompilationResult) -> str:
    if result.dependencies:
        dependencies = ('\n  Additional dependencies:\n'
                        '{bright}    {dependencies}{reset}').format(
            dependencies='\n    '.join(dep for dep in result.dependencies),
            bright=Style.BRIGHT,
            reset=Style.RESET_ALL)
    else:
        dependencies = ''

    return ('{bright}Compilation succeed{reset}:\n'
            '  target: {bright}{target}{reset}\n'
            '  files: {bright}{files}{reset}\n'
            '  took: {bright}{time:.2f}{reset} seconds{dependencies}').format(
        bright=Style.BRIGHT,
        reset=Style.RESET_ALL,
        target='{}.{}'.format(*result.target),
        files=result.files,
        time=result.time,
        dependencies=dependencies)


def warn(message: str) -> str:
    return '{bright}{red}WARN:{reset} {message}'.format(
        bright=Style.BRIGHT,
        red=Fore.RED,
        reset=Style.RESET_ALL,
        message=message)


def debug(message: str) -> str:
    return '{bright}{blue}DEBUG:{reset} {message}'.format(
        bright=Style.BRIGHT,
        blue=Fore.BLUE,
        reset=Style.RESET_ALL,
        message=message)
