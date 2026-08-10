# 先安装python3 -m pip install --upgrade pip setuptools wheel
# 然后运行python3 setup.py build_ext --inplace 要将py文件改为pyx
# setup.py
from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize

extensions = [
    Extension("ts_backtest_minute_com", ["ts_backtest_minute_com.pyx"])
]

setup(
    name="TS_BACK_TEST",
    ext_modules=cythonize(extensions),
)
