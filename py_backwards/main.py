from colorama import init

init()

from argparse import ArgumentParser
import sys
from .compiler import compile_files
from . import const, messages, exceptions


def main() -> int:
    parser = ArgumentParser(
        'py-backwards',
        description='Python to python compiler that allows you to use some '
                    'Python 3.6 features in older versions.')
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='input file or folder')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='output file or folder')
    parser.add_argument('-t', '--target', type=str,
                        required=True, choices=const.TARGETS.keys(),
                        help='target python version')
    args = parser.parse_args()

    try:
        result = compile_files(args.input, args.output,
                               const.TARGETS[args.target])
    except exceptions.CompilationError as e:
        print(messages.syntax_error(e), file=sys.stderr)
        return 1
    except exceptions.TransformationError as e:
        print(messages.transformation_error(e), file=sys.stderr)
        return 1
    except exceptions.InputDoesntExists:
        print(messages.input_doesnt_exists(args.input), file=sys.stderr)
        return 1
    except exceptions.InvalidInputOutput:
        print(messages.invalid_output(args.input, args.output),
              file=sys.stderr)
        return 1
    except PermissionError:
        print(messages.permission_error(args.output), file=sys.stderr)
        return 1

    print(messages.compilation_result(result))
    return 0
