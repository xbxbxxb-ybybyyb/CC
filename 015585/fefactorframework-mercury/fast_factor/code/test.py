import xfactor.runner.BasicRunner as Runner
from settings import RunMode
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
from xfactor.function_factor import *
from itertools import product

def func():
    para = '''a = 466'''
    exec(para)
    return a