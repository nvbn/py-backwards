import pytest
from types import ModuleType
from typed_ast.ast3 import parse
from typed_astunparse import unparse, dump


@pytest.fixture
def transform():
    def transform(transformer, before):
        tree = parse(before)
        try:
            transformer.transform(tree)
            return unparse(tree).strip()
        except:
            print('Before:')
            print(dump(parse(before)))
            print('After:')
            print(dump(tree))
            raise

    return transform


@pytest.fixture
def run_transformed(transform):
    def run_transformed(transformer, code):
        transformed = transform(transformer, code)
        splitted = transformed.split('\n')
        splitted[-1] = '__result = ' + splitted[-1]
        compiled = compile('\n'.join(splitted), '<generated>', 'exec')
        module = ModuleType('<generated>')
        exec(compiled, module.__dict__, )
        return module.__dict__['__result']

    return run_transformed
