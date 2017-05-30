import pytest
import os
from py_backwards.compiler import compile_files
from py_backwards.const import TARGETS

expected_output = '''
test variables: 1 2 3
test strings: hi there hi hi there! hi
test lists: [1, 2] [1, 2] [4, 1, 2, 5] [7, 8] [7, 8]
test dicts: [(1, 2)] [(1, 2), (u'a', u'b')] [(1, 2)] [(4, 5)] [(4, 5)]
test functions: 2 3 (1, (2, 3), {'b': 4}) (1, (2, 3), {u'b': u'c'})
test cycles: [0, 1, 2, 3, 4, u'!', 0, 1, 2]
test class: 2 2 3 4 20 30 4 4
test generators: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] [10] [10]
test for comprehension: [0, 1, 4, 9, 16] [1, 2, 3, 4, 5] {u'x': 1}
test exceptions: 1 3
test context manager: [10, 11]
test import override: Path PosixPath
'''.strip()

# TODO: test also on 3.0, 3.1 and 3.2
targets = [(version, target) for version, target in TARGETS.items()
           if target < (3, 0) or target > (3, 2)]


@pytest.mark.functional
@pytest.mark.parametrize('version, target', targets)
def test_compiled_code(spawnu, TIMEOUT, version, target):
    root = os.path.abspath(os.path.dirname(__file__))
    output = 'output_{}.py'.format(version)

    proc = spawnu('py_backwards/python-{}'.format(version),
                  'FROM python:{}'.format(version),
                  'bash')
    try:
        result = compile_files(os.path.join(root, 'input.py'),
                               os.path.join(root, output),
                               target)
        if result.dependencies:
            proc.sendline('pip install {}'.format(
                ' '.join(result.dependencies)))
            assert proc.expect_exact([TIMEOUT, 'Successfully installed'])

        proc.sendline('python{} src/tests/functional/{}'.format(
            version, output))
        # Output of `input.py` and converted:
        for line in expected_output.split('\n'):
            if target > (2, 7):
                line = line.replace("u'", "'")
            print(line)
            assert proc.expect_exact([TIMEOUT, line], timeout=10)
    finally:
        try:
            os.remove(os.path.join(root, output))
        except Exception as e:
            print("Can't delete compiled", e)
        proc.close(force=True)
