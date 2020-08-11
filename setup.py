"""Script for building cython code.

To be run as
>> python iris_setup.py build_ext --inplace

"""
import sys
from distutils.core import setup, Extension
from Cython.Build import cythonize

ext = Extension("iris.iristools",
                sources=["iris/iris.pyx"])
setup(
    name="iris",
    packages=['iris'],
    version='1.0.1',
    description='IRIS SHEAR tools',
    author='Jenna Ritvanen',
    author_email='jenna.ritvanen@fmi.fi',
    install_requires=[
        'numpy',
        'Cython',
        'matplotlib',
        'scipy'
    ],
    ext_modules=cythonize(
        ext, compiler_directives={'language_level': sys.version_info[0]})
)
