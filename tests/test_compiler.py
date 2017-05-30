from contextlib import contextmanager

import pytest
from unittest.mock import Mock
from io import StringIO
from py_backwards import compiler
from py_backwards.files import InputOutput
from py_backwards.exceptions import CompilationError


class TestCompileFiles(object):
    @pytest.fixture
    def input_output(self, mocker):
        mock = mocker.patch('py_backwards.compiler.get_input_output_paths')
        io = InputOutput(Mock(), Mock())
        mock.return_value = [io]
        return io

    def test_syntax_error(self, input_output):
        input_output.input.as_posix.return_value = 'test.py'
        input_output.input.open.return_value = StringIO('a b c d')
        with pytest.raises(CompilationError):
            compiler.compile_files('test.py', 'lib/test.py', (2, 7))

    def test_compile(self, input_output):
        output = StringIO()

        @contextmanager
        def output_f(*_):
            yield output

        input_output.input.as_posix.return_value = 'test.py'
        input_output.input.open.return_value = StringIO("print('hello world')")
        input_output.output.open = output_f

        result = compiler.compile_files('test.py', 'lib/test.py', (2, 7))
        assert result.files == 1
        assert result.target == (2, 7)
        assert result.time

        assert "print(u'hello world')" in output.getvalue()
