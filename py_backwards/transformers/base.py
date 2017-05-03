from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Union, Optional
from typed_ast import ast3 as ast
from ..types import CompilationTarget, TransformationResult
from ..utils.snippet import snippet, extend


class BaseTransformer(metaclass=ABCMeta):
    target = None  # type: CompilationTarget

    @classmethod
    @abstractmethod
    def transform(cls, tree: ast.AST) -> TransformationResult:
        ...


class BaseNodeTransformer(BaseTransformer, ast.NodeTransformer):
    dependencies = []  # type: List[str]

    def __init__(self, tree: ast.AST) -> None:
        super().__init__()
        self._tree = tree
        self._tree_changed = False

    @classmethod
    def transform(cls, tree: ast.AST) -> TransformationResult:
        inst = cls(tree)
        inst.visit(tree)
        return TransformationResult(tree, inst._tree_changed, cls.dependencies)


@snippet
def import_rewrite(previous, current):
    try:
        extend(previous)
    except ImportError:
        extend(current)


class BaseImportRewrite(BaseNodeTransformer):
    rewrites = []  # type: List[Tuple[str, str]]

    def _get_matched_rewrite(self, module: str) -> Optional[Tuple[str, str]]:
        for from_, to in self.rewrites:
            if module == from_ or module.startswith(from_ + '.'):
                return from_, to

        return None

    def _replace_import(self, node: ast.Import, from_: str, to: str) -> ast.Try:
        self._tree_changed = True

        rewrote_name = node.names[0].name.replace(from_, to, 1)
        import_as = node.names[0].asname or node.names[0].name.split('.')[-1]

        rewrote = ast.Import(names=[
            ast.alias(name=rewrote_name,
                      asname=import_as)])

        return import_rewrite.get_body(previous=node,  # type: ignore
                                       current=rewrote)[0]

    def visit_Import(self, node: ast.Import) -> Union[ast.Import, ast.Try]:
        rewrite = self._get_matched_rewrite(node.names[0].name)
        if rewrite:
            return self._replace_import(node, *rewrite)

        return self.generic_visit(node)

    def _replace_import_from(self, node: ast.ImportFrom, from_: str, to: str) -> ast.Try:
        self._tree_changed = True

        rewrote_module = node.module.replace(from_, to, 1)
        rewrote = ast.ImportFrom(module=rewrote_module,
                                 names=node.names,
                                 level=node.level)

        return import_rewrite.get_body(previous=node,  # type: ignore
                                       current=rewrote)[0]

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Union[ast.ImportFrom, ast.Try]:
        rewrite = self._get_matched_rewrite(node.module)
        if rewrite:
            return self._replace_import_from(node, *rewrite)

        return self.generic_visit(node)
