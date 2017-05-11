import pytest
from types import ModuleType
from typed_ast.ast3 import parse, dump
from astunparse import unparse, dump as dump_pretty


@pytest.fixture
def transform():
    def transform(transformer, before):
        tree = parse(before)
        try:
            transformer.transform(tree)
            return unparse(tree).strip()
        except:
            print('Before:')
            print(dump_pretty(parse(before)))
            print('After:')
            print(dump_pretty(tree))
            raise

    return transform


@pytest.fixture
def run_transformed(transform):
    def _get_latest_line(splitted):
        for n in range(-1, -1 - len(splitted), -1):
            if splitted[n][0] not in ')]} ':
                return n

    def run_transformed(transformer, code):
        transformed = transform(transformer, code)
        splitted = transformed.split('\n')
        latest_line = _get_latest_line(splitted)
        splitted[latest_line] = '__result = ' + splitted[latest_line]
        compiled = compile('\n'.join(splitted), '<generated>', 'exec')
        module = ModuleType('<generated>')
        exec(compiled, module.__dict__, )
        return module.__dict__['__result']

    return run_transformed


@pytest.fixture
def ast():
    def ast(code):
        return dump(parse(code))

    return ast
