from traceback import format_exc
from typed_ast import ast3 as ast
from typed_astunparse import unparse
from autopep8 import fix_code
from .dict_unpacking import DictUnpackingTransformer
from .formatted_values import FormattedValuesTransformer
from .functions_annotations import FunctionsAnnotationsTransformer
from .starred_unpacking import StarredUnpackingTransformer
from .variables_annotations import VariablesAnnotationsTransformer

transformers = [FormattedValuesTransformer,
                FunctionsAnnotationsTransformer,
                VariablesAnnotationsTransformer,
                StarredUnpackingTransformer,
                DictUnpackingTransformer]


class TransformationError(Exception):
    def __init__(self, filename, transformer, traceback):
        self.filename = filename
        self.transformer = transformer
        self.traceback = traceback


def transform(path, code, target):
    for transformer in transformers:
        tree = ast.parse(code, path)
        if transformer.target >= target:
            transformer().visit(tree)
        try:
            code = unparse(tree)
        except:
            raise TransformationError(path, transformer, format_exc())

    return fix_code(code)
