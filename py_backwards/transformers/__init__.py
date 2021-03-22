from typing import List, Type
from .walrus_operator import WalrusTransformer
from .walrus_operator import FallbackWalrusTransformer
from .posonlyargs import PosOnlyArgTransformer
from .dict_unpacking import DictUnpackingTransformer
from .formatted_values import FormattedValuesTransformer
from .functions_annotations import FunctionsAnnotationsTransformer
from .starred_unpacking import StarredUnpackingTransformer
from .variables_annotations import VariablesAnnotationsTransformer
from .matrix_multiplication import MatMultTransformer
from .async_generators import AsyncGeneratorTransformer
from .async_for import AsyncForTransformer
from .async_with import AsyncWithTransformer
from .async_functions import AsyncFunctionTransformer
from .yield_from import YieldFromTransformer
from .return_from_generator import ReturnFromGeneratorTransformer
from .python2_future import Python2FutureTransformer
from .python2_future import Python25FutureTransformer
from .nonlocal_statement import NonlocalStatementTransformer
from .class_bool_method import ClassBoolMethodTransformer
from .super_without_arguments import SuperWithoutArgumentsTransformer
from .class_without_bases import ClassWithoutBasesTransformer
from .import_pathlib import ImportPathlibTransformer
from .six_moves import SixMovesTransformer
from .metaclass import MetaclassTransformer
from .kwargs import KwArgTransformer
from .kwonlyargs import KwOnlyArgTransformer
from .byte_literals import ByteLiteralTransformer
from .import_dbm import ImportDbmTransformer
from .unicode_identifiers import UnicodeIdentifierTransformer
from .set_literals import SetLiteralTransformer
from .dict_comprehension import DictComprehensionTransformer
from .class_decorators import ClassDecoratorTransformer
from .except_as import ExceptAsTransformer
from .raise_from import RaiseFromTransformer
from .print_function import PrintFunctionTransformer
from .base import BaseTransformer

transformers = [
    # 3.7
    WalrusTransformer,
    FallbackWalrusTransformer,
    PosOnlyArgTransformer,
    # 3.5
    VariablesAnnotationsTransformer,
    FormattedValuesTransformer,
    AsyncGeneratorTransformer,
    # 3.4
    DictUnpackingTransformer,
    StarredUnpackingTransformer,
    MatMultTransformer,
    AsyncForTransformer,
    AsyncWithTransformer,
    AsyncFunctionTransformer,
    # 3.2
    YieldFromTransformer,
    ReturnFromGeneratorTransformer,
    # 2.7
    FunctionsAnnotationsTransformer,
    SuperWithoutArgumentsTransformer,
    ClassWithoutBasesTransformer,
    ImportPathlibTransformer,
    SixMovesTransformer,
    ClassBoolMethodTransformer,
    MetaclassTransformer,
    ImportDbmTransformer,
    NonlocalStatementTransformer,
    RaiseFromTransformer,
    KwOnlyArgTransformer,
    UnicodeIdentifierTransformer,
    # 2.5
    SetLiteralTransformer,
    PrintFunctionTransformer,
    ExceptAsTransformer,
    DictComprehensionTransformer,
    ClassDecoratorTransformer,
    KwArgTransformer,

    # These transformers should be last and in this order to prevent conflicts.
    ByteLiteralTransformer,     # 2.5
    Python2FutureTransformer,   # 2.7
    Python25FutureTransformer,  # 2.5
]  # type: List[Type[BaseTransformer]]
