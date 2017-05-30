# Py-backwards [![Build Status](https://travis-ci.org/nvbn/py-backwards.svg?branch=master)](https://travis-ci.org/nvbn/py-backwards)

Python to python compiler that allows you to use some Python 3.6 features in older versions, you can try it in [the online demo](https://py-backwards.herokuapp.com/).

Requires Python 3.3+ to run, can compile down to 2.7.

## Supported features

Target 3.5:
* [formatted string literals](https://docs.python.org/3/whatsnew/3.6.html#pep-498-formatted-string-literals) like `f'hi {x}'`
* [variables annotations](https://docs.python.org/3/whatsnew/3.6.html#whatsnew36-pep526) like `x: int = 10` and `x: int`
* [underscores in numeric literals](https://docs.python.org/3/whatsnew/3.6.html#pep-515-underscores-in-numeric-literals) like `1_000_000` (works automatically)

Target 3.4:
* [starred unpacking](https://docs.python.org/3/whatsnew/3.5.html#pep-448-additional-unpacking-generalizations) like `[*range(1, 5), *range(10, 15)]` and `print(*[1, 2], 3, *[4, 5])`
* [dict unpacking](https://docs.python.org/3/whatsnew/3.5.html#pep-448-additional-unpacking-generalizations) like `{1: 2, **{3: 4}}`

Target 3.3:
* import [pathlib2](https://pypi.python.org/pypi/pathlib2/) instead of pathlib

Target 3.2:
* [yield from](https://docs.python.org/3/whatsnew/3.3.html#pep-380)
* [return from generator](https://docs.python.org/3/whatsnew/3.3.html#pep-380)

Target 2.7:
* [functions annotations](https://www.python.org/dev/peps/pep-3107/) like `def fn(a: int) -> str`
* [imports from `__future__`](https://docs.python.org/3/howto/pyporting.html#prevent-compatibility-regressions)
* [super without arguments](https://www.python.org/dev/peps/pep-3135/)
* classes without base like `class A: pass`
* imports from [six moves](https://pythonhosted.org/six/#module-six.moves)
* metaclass
* string/unicode literals (works automatically)
* `str` to `unicode`

For example, if you have some python 3.6 code, like:

```python
def returning_range(x: int):
    yield from range(x)
    return x


def x_printer(x):
    val: int
    val = yield from returning_range(x)
    print(f'val {val}')


def formatter(x: int) -> dict:
    items: list = [*x_printer(x), x]
    print(*items, *items)
    return {'items': items}


result = {'x': 10, **formatter(10)}
print(result)


class NumberManager:
    def ten(self):
        return 10

    @classmethod
    def eleven(cls):
        return 11


class ImportantNumberManager(NumberManager):
    def ten(self):
        return super().ten()

    @classmethod
    def eleven(cls):
        return super().eleven()


print(ImportantNumberManager().ten())
print(ImportantNumberManager.eleven())
```

You can compile it for python 2.7 with:

```bash
➜ py-backwards -i input.py -o output.py -t 2.7
```

Got some [ugly code](https://gist.github.com/nvbn/51b1536dc05bddc09439f848461cef6a) and ensure that it works:

```bash
➜ python3.6 input.py
val 10
0 1 2 3 4 5 6 7 8 9 10 0 1 2 3 4 5 6 7 8 9 10
{'x': 10, 'items': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
10
11
➜ python2 output.py                           
val 10
0 1 2 3 4 5 6 7 8 9 10 0 1 2 3 4 5 6 7 8 9 10
{'x': 10, 'items': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
10
11
```

## Usage

Installation:

```bash
pip install py-backwards
```

Compile code:

```bash
py-backwards -i src -o compiled -t 2.7
```

### Testing compiled code

For testing compiled code with each supported python version you can use [tox](https://tox.readthedocs.io/en/latest/)
and [tox-py-backwards](https://github.com/nvbn/tox-py-backwards). You need to install them:

```bash
pip install tox tox-py-backwards
```

Fill `tox.ini` (`py_backwards = true` in `testenv` section enables py-backwards), like:

```ini
[tox]
envlist = py27,py33,py34,py35,py36

[testenv]
deps = pytest
commands = py.test
py_backwards = true
```

And run tests with:

```bash
tox
```

### Distributing compiled code

For distributing packages compiled with py-backwards you can use [py-backwards-packager](https://github.com/nvbn/py-backwards-packager).
Install it with:

```python
pip install py-backwards-packager
```

And change `setup` import in `setup.py` to:
 
```python
try:
    from py_backwards_packager import setup
except ImportError:
    from setuptools import setup
```

By default all targets enabled, but you can limit them with:
 
```python
setup(...,
      py_backwards_targets=['2.7', '3.3'])
```

After that your code will be automatically compiled on `bdist` and `bdist_wheel`.

### Running on systems without Python 3.3+

You can use docker for running py-backwards on systems without Python 3.3+, for example
for testing on travis-ci with Python 2.7:

```bash
docker run -v $(pwd):/data/ nvbn/py-backwards -i example -o out -t 2.7
```

## Development

Setup:

```bash
pip install .
python setup.py develop
pip install -r requirements.txt
```

Run tests:

```bash
 py.test -vvvv --capture=sys --enable-functional
```

Run tests on systems without docker:

```bash
 py.test -vvvv
```

## Writing code transformers

First of all, you need to inherit from `BaseTransformer`, `BaseNodeTransformer` (if you want to use
[NodeTransfromer](https://docs.python.org/3/library/ast.html#ast.NodeTransformer) interface),
or `BaseImportRewrite` (if you want just to change import).

If you use `BaseTransformer`, override class method `def transform(cls, tree: ast.AST) -> TransformationResult`, like:

```python
from ..types import TransformationResult
from .base import BaseTransformer


class MyTransformer(BaseTransformer):
    @classmethod
    def transform(cls, tree: ast.AST) -> TransformationResult:
        return TransformationResult(tree=tree,
                                    tree_changed=True,
                                    dependencies=[])
```

If you use `BaseNodeTransformer`, override `visit_*` methods, for simplification this class
have a whole tree in `self._tree`, you should also set `self._tree_changed = True` if the tree
was changed:

```python
from .base import BaseNodeTransformer


class MyTransformer(BaseNodeTransformer):
    dependencies = []  # additional dependencies

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        self._tree_changed = True  # Mark that transformer changed tree
        return self.generic_visit(node)
```

If you use `BaseImportRewrite`, just override `rewrites`, like:

```python
from .base import BaseImportRewrite


class MyTransformer(BaseImportRewrite):
    dependencies = ['pathlib2']

    rewrites = [('pathlib', 'pathlib2')]
```

After that you need to add your transformer to `transformers.__init__.transformers`.

It's hard to write code in AST, because of that we have [snippets](https://github.com/nvbn/py-backwards/blob/master/py_backwards/utils/snippet.py#L102):

```python
from ..utils.snippet import snippet, let, extend


@snippet
def my_snippet(class_name, class_body):
    class class_name:  # will be replaced with `class_name`
        extend(class_body)  # body of the class will be extended with `class_body`
        
        def fn(self):
            let(x)  # x will be replaced everywhere with unique name, like `_py_backwards_x_1`
            x = 10
            return x
```

And you can easily get content of snippet with:

```python
my_snippet.get_body(class_name='MyClass',
                    class_body=[ast.Expr(...), ...])
```

Also please look at [tree utils](https://github.com/nvbn/py-backwards/blob/master/py_backwards/utils/tree.py),
it contains such useful functions like `find`, `get_parent` and etc.

## Related projects

* [py-backwards-astunparse](https://github.com/nvbn/py-backwards-astunparse)
* [tox-py-backwards](https://github.com/nvbn/tox-py-backwards)
* [py-backwards-packager](https://github.com/nvbn/py-backwards-packager)
* [pytest-docker-pexpect](https://github.com/nvbn/pytest-docker-pexpect)

## License MIT
