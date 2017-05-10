from colorama import init

init()

from argparse import ArgumentParser
import sys
from .compiler import compile_files
from .conf import init_settings
from . import const, messages, exceptions


def main() -> int:
    parser = ArgumentParser(
        'py-backwards',
        description='Python to python compiler that allows you to use some '
                    'Python 3.6 features in older versions.')
    parser.add_argument('-i', '--input', type=str, nargs='+', required=True,
                        help='input file or folder')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='output file or folder')
    parser.add_argument('-t', '--target', type=str,
                        required=True, choices=const.TARGETS.keys(),
                        help='target python version')
    parser.add_argument('-r', '--root', type=str, required=False,
                        help='sources root')
    parser.add_argument('-d', '--debug', action='store_true', required=False,
                        help='enable debug output')
    args = parser.parse_args()
    init_settings(args)

    try:
        for input_ in args.input:
            result = compile_files(input_, args.output,
                                   const.TARGETS[args.target],
                                   args.root)
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
