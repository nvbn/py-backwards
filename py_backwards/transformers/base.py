from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Union, Optional, Iterable, Dict
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

    def _get_matched_rewrite(self, name: Optional[str]) -> Optional[Tuple[str, str]]:
        """Returns rewrite for module name."""
        if name is None:
            return None

        for from_, to in self.rewrites:
            if name == from_ or name.startswith(from_ + '.'):
                return from_, to

        return None

    def _replace_import(self, node: ast.Import, from_: str, to: str) -> ast.Try:
        """Replace import with try/except with old and new import."""
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

    def _replace_import_from_module(self, node: ast.ImportFrom, from_: str, to: str) -> ast.Try:
        """Replaces import from with try/except with old and new import module."""
        self._tree_changed = True

        rewrote_module = node.module.replace(from_, to, 1)
        rewrote = ast.ImportFrom(module=rewrote_module,
                                 names=node.names,
                                 level=node.level)

        return import_rewrite.get_body(previous=node,  # type: ignore
                                       current=rewrote)[0]

    def _get_names_to_replace(self, node: ast.ImportFrom) -> Iterable[Tuple[str, Tuple[str, str]]]:
        """Finds names/aliases to replace."""
        for alias in node.names:
            full_name = '{}.{}'.format(node.module, alias.name)
            if alias.name != '*':
                rewrite = self._get_matched_rewrite(full_name)
                if rewrite:
                    yield (full_name, rewrite)

    def _get_replaced_import_from_part(self, node: ast.ImportFrom, alias: ast.alias,
                                       names_to_replace: Dict[str, Tuple[str, str]]) -> ast.ImportFrom:
        """Returns import from statement with changed module or alias."""
        full_name = '{}.{}'.format(node.module, alias.name)
        if full_name in names_to_replace:
            full_name = full_name.replace(names_to_replace[full_name][0],
                                          names_to_replace[full_name][1],
                                          1)
        module_name = '.'.join(full_name.split('.')[:-1])
        name = full_name.split('.')[-1]
        return ast.ImportFrom(
            module=module_name,
            names=[ast.alias(name=name,
                             asname=alias.asname or alias.name)],
            level=node.level)

    def _replace_import_from_names(self, node: ast.ImportFrom,
                                   names_to_replace: Dict[str, Tuple[str, str]]) -> ast.Try:
        """Replaces import from with try/except with old and new 
        import module and names.
        
        """
        self._tree_changed = True

        rewrotes = [
            self._get_replaced_import_from_part(node, alias, names_to_replace)
            for alias in node.names]

        return import_rewrite.get_body(previous=node,  # type: ignore
                                       current=rewrotes)[0]

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Union[ast.ImportFrom, ast.Try]:
        rewrite = self._get_matched_rewrite(node.module)
        if rewrite:
            return self._replace_import_from_module(node, *rewrite)

        names_to_replace = dict(self._get_names_to_replace(node))
        if names_to_replace:
            return self._replace_import_from_names(node, names_to_replace)

        return self.generic_visit(node)
