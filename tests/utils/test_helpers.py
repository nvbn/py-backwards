from py_backwards.utils.helpers import VariablesGenerator, eager


def test_eager():
    @eager
    def fn():
        yield 1
        yield 2
        yield 3

    assert fn() == [1, 2, 3]


def test_variables_generator():
    assert VariablesGenerator.generate('x') == '_py_backwards_x_0'
    assert VariablesGenerator.generate('x') == '_py_backwards_x_1'
