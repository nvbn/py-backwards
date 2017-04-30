from traceback import format_exc
from typing import List, Type
from typed_ast import ast3 as ast
from typed_astunparse import unparse, dump
from autopep8 import fix_code
from ..types import CompilationTarget
from .dict_unpacking import DictUnpackingTransformer
from .formatted_values import FormattedValuesTransformer
from .functions_annotations import FunctionsAnnotationsTransformer
from .starred_unpacking import StarredUnpackingTransformer
from .variables_annotations import VariablesAnnotationsTransformer
from .yield_from import YieldFromTransformer
from .return_from_generator import ReturnFromGeneratorTransformer
from .python2_future import Python2FutureTransformer
from .super_without_arguments import SuperWithoutArgumentsTransformer
from .class_without_bases import ClassWithoutBasesTransformer
from .base import BaseTransformer

transformers = [DictUnpackingTransformer,
                StarredUnpackingTransformer,
                FormattedValuesTransformer,
                FunctionsAnnotationsTransformer,
                VariablesAnnotationsTransformer,
                YieldFromTransformer,
                ReturnFromGeneratorTransformer,
                Python2FutureTransformer,
                SuperWithoutArgumentsTransformer,
                ClassWithoutBasesTransformer]  # type: List[Type[BaseTransformer]]


def transform(path: str, code: str, target: CompilationTarget) -> str:
    """Applies all transformation for passed target."""
    from ..exceptions import TransformationError

    for transformer in transformers:
        tree = ast.parse(code, path)
        if transformer.target >= target:
            tree = transformer.transform(tree)
        try:
            code = unparse(tree)
        except:
            raise TransformationError(path, transformer,
                                      dump(tree), format_exc())

    return fix_code(code)
