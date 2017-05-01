import pytest
import os
from py_backwards.compiler import compile_files
from py_backwards.const import TARGETS


expected_output = '''
1 2 3 4
val 10
0 1 2 3 4 5 6 7 8 9 10 0 1 2 3 4 5 6 7 8 9 10
{'x': 10, 'items': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
x
items
2
1
10
11
'''.strip()


@pytest.mark.functional
@pytest.mark.parametrize('version, target', TARGETS.items())
def test_compiled_code(spawnu, TIMEOUT, version, target):
    root = os.path.abspath(os.path.dirname(__file__))
    output = 'output_{}.py'.format(version)

    try:
        compile_files(os.path.join(root, 'input.py'),
                      os.path.join(root, output),
                      target)

        proc = spawnu('py_backwards/python-{}'.format(version),
                      'FROM python:{}'.format(version),
                      'bash')
        proc.sendline('python{} src/tests/functional/{}'.format(
            version, output))
        # Output of `input.py` and converted:
        for line in expected_output.split('\n'):
            assert proc.expect([TIMEOUT, line.strip()])
    finally:
        try:
            os.remove(output)
        except Exception as e:
            print("Can't delete compiled", e)
