# Py-backwards [![Build Status](https://travis-ci.org/nvbn/py-backwards.svg?branch=master)](https://travis-ci.org/nvbn/py-backwards)

Python to python compiler that allows you to use some Python 3.6 features in older versions.

Requires Python 3.3+ to run, can compile down to 2.7.

## Supported features:

Target 3.5:
* [formatted string literals](https://docs.python.org/3/whatsnew/3.6.html#pep-498-formatted-string-literals) like `f'hi {x}'`
* [variables annotations](https://docs.python.org/3/whatsnew/3.6.html#whatsnew36-pep526) like `x: int = 10` and `x: int`
* [underscores in numeric literals](https://docs.python.org/3/whatsnew/3.6.html#pep-515-underscores-in-numeric-literals) like `1_000_000` (works automatically)

Target 3.4:
* [starred unpacking](https://docs.python.org/3/whatsnew/3.5.html#pep-448-additional-unpacking-generalizations) like `[*range(1, 5), *range(10, 15)]` and `print(*[1, 2], 3, *[4, 5])`
* [dict unpacking](https://docs.python.org/3/whatsnew/3.5.html#pep-448-additional-unpacking-generalizations) like `{1: 2, **{3: 4}}`

Target 3.2:
* [yield from](https://docs.python.org/3/whatsnew/3.3.html#pep-380)
* [return from generator](https://docs.python.org/3/whatsnew/3.3.html#pep-380)

Target 2.7:
* [functions annotations](https://www.python.org/dev/peps/pep-3107/) like `def fn(a: int) -> str`
* [imports from __future__](https://docs.python.org/3/howto/pyporting.html#prevent-compatibility-regressions)
* [super without arguments](https://www.python.org/dev/peps/pep-3135/)

## Usage

Installation:

```bash
pip install py-backwards
```

Usage:

```bash
py-backwards -i src -o compiled -t 2.7
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
py.test
```

## License MIT
