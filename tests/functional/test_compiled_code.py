import pytest
import os
from py_backwards.compiler import compile_files
from py_backwards.const import TARGETS

expected_output = '''
1 2 3 4
val 10
0 1 2 3 4 5 6 7 8 9 10 0 1 2 3 4 5 6 7 8 9 10
items [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
x 10
2
1
10
11
works
101 102
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
            assert proc.expect_exact([TIMEOUT, line], timeout=1)
    finally:
        try:
            os.remove(os.path.join(root, output))
        except Exception as e:
            print("Can't delete compiled", e)
        proc.close(force=True)
