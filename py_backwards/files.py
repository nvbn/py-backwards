from typing import Iterable, Optional

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path  # type: ignore

from .types import InputOutput
from .exceptions import InvalidInputOutput, InputDoesntExists


def get_input_output_paths(input_: str, output: str,
                           root: Optional[str]) -> Iterable[InputOutput]:
    """Get input/output paths pairs."""
    if output.endswith('.py') and not input_.endswith('.py'):
        raise InvalidInputOutput

    if not Path(input_).exists():
        raise InputDoesntExists

    if input_.endswith('.py'):
        if output.endswith('.py'):
            yield InputOutput(Path(input_), Path(output))
        else:
            input_path = Path(input_)
            if root is None:
                output_path = Path(output).joinpath(input_path.name)
            else:
                output_path = Path(output).joinpath(input_path.relative_to(root))
            yield InputOutput(input_path, output_path)
    else:
        output_path = Path(output)
        input_path = Path(input_)
        root_path = input_path if root is None else Path(root)
        for child_input in input_path.glob('**/*.py'):
            child_output = output_path.joinpath(
                child_input.relative_to(root_path))
            yield InputOutput(child_input, child_output)
