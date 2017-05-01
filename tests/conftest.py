import pytest
from typed_ast import ast3 as ast
from py_backwards.utils.helpers import VariablesGenerator, get_source


@pytest.fixture(autouse=True)
def reset_variables_generator():
    VariablesGenerator._counter = 0


@pytest.fixture
def as_str():
    def as_str(fn):
        return get_source(fn).strip()

    return as_str


@pytest.fixture
def as_ast():
    def as_ast(fn):
        return ast.parse(get_source(fn))

    return as_ast
