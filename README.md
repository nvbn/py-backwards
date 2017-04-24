# Py-backwards

Translates python code for older versions.

Supported features:

* formatted strings like `f'hi {x}'`;
* type annotations like `x: int = 10`, `def fn(a: int) -> str` and `x: int`.

## Usage

Installation:

```bash
pip install py-backwards
```

Usage:

```bash
py-backwards -i src -o compiled
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
