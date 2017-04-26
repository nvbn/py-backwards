from typing import NamedTuple, Tuple
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path  # type: ignore

# Target python version
CompilationTarget = Tuple[int, int]

# Information about compilation
CompilationResult = NamedTuple('CompilationResult',
                               [('files', int),
                                ('time', float),
                                ('target', Tuple[int, int])])

# Input/output pair
InputOutput = NamedTuple('InputOutput', [('input', Path),
                                         ('output', Path)])
