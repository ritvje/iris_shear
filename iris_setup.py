"""Script for building cython code.

To be run as
>> python iris_setup.py build_ext --inplace

"""
import sys
from distutils.core import setup, Extension
from Cython.Build import cythonize

ext = Extension("iris_tools",
                sources=["iris.pyx"])
setup(
    ext_modules=cythonize(ext, compiler_directives={
                          'language_level': sys.version_info[0]})
)
