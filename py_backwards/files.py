from collections import namedtuple

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

InputOutput = namedtuple('InputOutput', ('input', 'output'))


class InvalidInputOutput(Exception):
    """Raises when input is a directory, but output is a file."""


def get_input_output_paths(input_, output):
    if output.endswith('.py') and not input_.endswith('.py'):
        raise InvalidInputOutput(
            "Output should be directory when input is directory")

    if not Path(input_).exists():
        raise InvalidInputOutput("Input doesn't exists")

    if input_.endswith('.py'):
        if output.endswith('.py'):
            yield InputOutput(Path(input_), Path(output))
        else:
            input_path = Path(input_)
            output_path = Path(output).joinpath(input_path.name)
            yield InputOutput(input_path, output_path)
    else:
        output_path = Path(output)
        input_path = Path(input_)
        for child_input in input_path.glob('**/*.py'):
            child_output = output_path.joinpath(
                child_input.relative_to(input_path))
            yield InputOutput(child_input, child_output)
