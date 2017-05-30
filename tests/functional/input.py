"""This file contains all supported python constructions."""


# Variables:

def test_variables():
    a = 1
    b: int = 2
    c: int
    c = 3
    print('test variables:', a, b, c)


test_variables()


# Strings:

def test_strings():
    a = 'hi'
    e = f'{a}'
    b: str = 'there'
    c = f'{a}'
    d = f'{a} {b}!'
    print('test strings:', a, b, c, d, e)


test_strings()


# Lists:

def test_lists():
    a = [1, 2]
    b = [*a]
    c = [4, *b, 5]
    d: list = [7, 8]
    e: list = [*d]
    print('test lists:', a, b, c, d, e)


test_lists()


# Dicts:

def test_dicts():
    a = {1: 2}
    b = {'a': 'b', **a}
    c = {**a}
    d: dict = {4: 5}
    e: dict = {**d}
    key = '{0[0]}-{0[0]}'.format
    print('test dicts:',
          sorted(a.items(), key=key),
          sorted(b.items(), key=key),
          sorted(c.items(), key=key),
          sorted(d.items(), key=key),
          sorted(e.items(), key=key))


test_dicts()


# Functions:

def test_functions():
    def inc(fn):
        def wrapper(x):
            return x + 1

        return wrapper

    @inc
    def fn_a(a: int) -> int:
        return a

    @inc
    def fn_b(b):
        return b

    def fn_c(a, *args, **kwargs):
        return a, args, kwargs

    print('test functions:', fn_a(1), fn_b(2), fn_c(1, 2, 3, b=4),
          fn_c(*[1, 2, 3], **{'b': 'c'}))


test_functions()


# Cycles:

def test_cycles():
    xs = []
    for x in range(5):
        xs.append(x)

    for y in []:
        xs.append(y)
    else:
        xs.append('!')

    m = 0
    while m < 3:
        xs.append(m)
        m += 1

    print('test cycles:', xs)


test_cycles()


# Class:


def test_class():
    class Base(type):
        def base_method(cls, x: int) -> int:
            return x + 1

    class First(metaclass=Base):
        def method_a(self):
            return 2

        @classmethod
        def method_b(cls):
            return 3

        @staticmethod
        def method_c():
            return 4

    class Second(First):
        def method_a(self):
            return super().method_a() * 10

        @classmethod
        def method_b(cls):
            return super().method_b() * 10

    print('test class:', First.base_method(1), First().method_a(),
          First.method_b(), First.method_c(), Second().method_a(),
          Second.method_b(), Second.method_c(), Second().method_c())


test_class()


# Generators:

def test_generators():
    def gen_a():
        for x in range(10):
            yield x

    def gen_b():
        yield from gen_a()

    def gen_c():
        a = yield 10
        return a

    def gen_d():
        a = yield from gen_c()

    print('test generators:', list(gen_a()), list(gen_b()), list(gen_c()),
          list(gen_d()))


test_generators()


# For-comprehension:

def test_for_comprehension():
    xs = [x ** 2 for x in range(5)]
    ys = (y + 1 for y in range(5))
    zs = {a: b for a, b in ({'x': 1}).items()}
    print('test for comprehension:', xs, list(ys), zs)


test_for_comprehension()


# Exceptions:

def test_exceptions():
    result = []
    try:
        raise Exception()
    except Exception:
        result.append(1)
    else:
        result.append(2)
    finally:
        result.append(3)
    print('test exceptions:', *result)


test_exceptions()


# Context manager:

def test_context_manager():
    result = []
    from contextlib import contextmanager

    @contextmanager
    def manager(x):
        try:
            yield x
        finally:
            result.append(x + 1)

    with manager(10) as v:
        result.append(v)

    print('test context manager:', result)


test_context_manager()


# Imports:

def test_imports():
    from pathlib import Path
    import pathlib
    print('test import override:', Path.__name__, pathlib.PosixPath.__name__)


test_imports()
