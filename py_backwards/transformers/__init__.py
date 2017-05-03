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
