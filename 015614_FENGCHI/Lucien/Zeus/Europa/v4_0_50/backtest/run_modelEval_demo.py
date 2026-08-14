# coding: utf-8
# Author：fengchi863
# Date ：2023/8/8 10:20

import os
from itertools import product
from LucienUtil.SpeedUtil import SpeedUtil

period_list = ['period1', 'period2', 'period3', 'period4', 'period5']
# period_list = ['period6']
testfit_list = ['test']
# testfit_list = ['fit']

param_list = list(product(period_list, testfit_list))

def wrapper(_param_list):
    for param_tuple in _param_list:
        PERIOD = param_tuple[0]
        testfit = param_tuple[1]
        os.system(f'python3 /data/user/015614/Lucien/Zeus/Europa/v4_0_50/backtest/modelEval_demo.py {PERIOD} {testfit}')

SpeedUtil.multiprocess(1, wrapper, param_list)
# wrapper(param_list)