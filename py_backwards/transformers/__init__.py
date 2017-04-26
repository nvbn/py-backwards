from typed_ast import ast3 as ast
from astunparse import unparse
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


def transform(code, target):
    tree = ast.parse(code)
    for transformer in transformers:
        if transformer.target >= target:
            transformer().visit(tree)
    return fix_code(unparse(tree))
