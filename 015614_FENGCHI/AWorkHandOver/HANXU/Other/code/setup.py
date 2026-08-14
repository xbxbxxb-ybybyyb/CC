from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize(["tradeDate.py", "FactorList.py", "operators.py", "FactorTest.py"]))

#cd /data/user/015836/HANXU/alphaResearch/dataUpdate/machine/code/
#python3 setup.py build_ext --inplace


