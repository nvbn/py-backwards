import pytest

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

from py_backwards.exceptions import InvalidInputOutput, InputDoesntExists
from py_backwards import files


class TestGetInputPath(object):
    @pytest.fixture(autouse=True)
    def exists(self, mocker):
        exists_mock = mocker.patch('py_backwards.files.Path.exists')
        exists_mock.return_value = True
        return exists_mock

    def test_dir_to_file(self):
        with pytest.raises(InvalidInputOutput):
            list(files.get_input_output_paths('src/', 'out.py', None))

    def test_non_exists_input(self, exists):
        exists.return_value = False
        with pytest.raises(InputDoesntExists):
            list(files.get_input_output_paths('src/', 'out/', None))

    def test_file_to_dir(self):
        assert list(files.get_input_output_paths('test.py', 'out/', None)) == [
            files.InputOutput(Path('test.py'), Path('out/test.py'))]

    def test_file_to_file(self):
        assert list(files.get_input_output_paths('test.py', 'out.py', None)) == [
            files.InputOutput(Path('test.py'), Path('out.py'))]

    def test_dir_to_dir(self, mocker):
        glob_mock = mocker.patch('py_backwards.files.Path.glob')
        glob_mock.return_value = [Path('src/main.py'), Path('src/const/const.py')]
        assert list(files.get_input_output_paths('src', 'out', None)) == [
            files.InputOutput(Path('src/main.py'), Path('out/main.py')),
            files.InputOutput(Path('src/const/const.py'), Path('out/const/const.py'))]

    def test_file_to_dir_with_root(self):
        paths = list(files.get_input_output_paths('project/src/test.py',
                                                  'out',
                                                  'project'))
        assert paths == [files.InputOutput(Path('project/src/test.py'),
                                           Path('out/src/test.py'))]

    def test_dir_to_dir_with_root(self, mocker):
        glob_mock = mocker.patch('py_backwards.files.Path.glob')
        glob_mock.return_value = [Path('project/src/main.py'),
                                  Path('project/src/const/const.py')]
        paths = list(files.get_input_output_paths('project', 'out', 'project'))
        assert paths == [
            files.InputOutput(Path('project/src/main.py'),
                              Path('out/src/main.py')),
            files.InputOutput(Path('project/src/const/const.py'),
                              Path('out/src/const/const.py'))]
