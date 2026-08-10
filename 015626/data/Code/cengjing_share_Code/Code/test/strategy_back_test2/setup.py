# setup.py
from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize

extensions = [
    Extension("back_test_tick_multisignal_order", ["back_test_tick_multisignal_order.pyx"])
]

setup(
    name="TS_BACK_TEST",
    ext_modules=cythonize(extensions),
)
