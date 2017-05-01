from typed_ast.ast3 import parse
from typed_astunparse import unparse, dump


def transform(transformer, before):
    tree = parse(before)
    try:
        transformer().visit(tree)
        return unparse(tree).strip()
    except:
        print('Before:')
        print(dump(parse(before)))
        print('After:')
        print(dump(tree))
        raise


def run(transformer, code):
    transformed = transform(transformer, code)
    splitted = transformed.split('\n')
    splitted[-1] = '__result = ' + splitted[-1]
    locals_ = {}
    exec('\n'.join(splitted), {}, locals_)
    return locals_['__result']
