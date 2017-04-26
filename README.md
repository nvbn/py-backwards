# Py-backwards

Python to python compiler that allows you to use Python 3.6 features in older versions.

Supported features:

* formatted strings like `f'hi {x}'`;
* functions annotations like `def fn(a: int) -> str`;
* variables annotations like `x: int = 10` and `x: int`.

Requires Python 3.3+.

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
python setup.py develop
pip install -r requirements.txt
```

Run tests:

```bash
py.test
```

## License MIT
