from typing import List, Type
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
from .import_pathlib import ImportPathlibTransformer
from .six_moves import SixMovesTransformer
from .metaclass import MetaclassTransformer
from .base import BaseTransformer

transformers = [
    # 3.6
    DictUnpackingTransformer,  # https://github.com/nvbn/py-backwards/issues/11
    # 3.5
    VariablesAnnotationsTransformer,
    FormattedValuesTransformer,
    # 3.4
    StarredUnpackingTransformer,
    # 3.2
    YieldFromTransformer,
    ReturnFromGeneratorTransformer,
    # 2.7
    FunctionsAnnotationsTransformer,
    SuperWithoutArgumentsTransformer,
    ClassWithoutBasesTransformer,
    ImportPathlibTransformer,
    SixMovesTransformer,
    MetaclassTransformer,
    Python2FutureTransformer,  # always should be the last transformer
]  # type: List[Type[BaseTransformer]]
