# coding: utf-8
# Author：fengchi863
# Date ：2020/3/30 13:20

import pandas as pd, numpy as np
import copy
from util import *
from dataApi.interdayTest import FactorBackTest

'''
因子逻辑：
根据前N日换手率分位数进行筛选
'''
root_path = '/data/group/800319/junkData/temp_factor_by_fc/'

start_date = 20170101
end_date = 20191231
ref_days = 10
N = 3 # 前N日换手率分位数
index_code = 'ZZ500'

turn = get_daily_1factor('free_turn')
turn_pre_n_sum = turn.rolling(N).sum().shift(1).loc[start_date:end_date]

print('开始进行回测')
factor = turn_pre_n_sum
fbt = FactorBackTest(group=10)
fbt.load_factor(factor)
fbt.calc_group_ret()
print(fbt.calc_ic().mean())
fbt.report(factor=factor, address=root_path, file_name='junk_factor')

'''
N=1: -0.0137
N=2: -0.0131
N=3: -0.0139

'''