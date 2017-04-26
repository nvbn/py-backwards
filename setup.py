#!/usr/bin/env python
from setuptools import setup, find_packages

VERSION = '0.1'

install_requires = ['typed-ast', 'astunparse', 'autopep8']
extras_require = {':python_version<"3.4"': ['pathlib2']}

setup(name='py-backwards',
      version=VERSION,
      description="Translates python code for older versions",
      author='Vladimir Iakovlev',
      author_email='nvbn.rm@gmail.com',
      url='https://github.com/nvbn/py-backwards',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'example', 'tests', 'tests.*']),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      extras_require=extras_require,
      entry_points={'console_scripts': [
          'py-backwards = py_backwards.main:main']})