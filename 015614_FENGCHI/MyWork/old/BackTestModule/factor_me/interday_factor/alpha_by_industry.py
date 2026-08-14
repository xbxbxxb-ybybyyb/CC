# coding: utf-8
# Author：fengchi863
# Date ：2020/3/27 10:48

import pandas as pd, numpy as np
import copy
from util import *
from dataApi.interdayTest import FactorBackTest

'''
因子逻辑：
根据前N日行业内超额分位数来进行定义
N取了1、2、3、4、5、10
'''
root_path = '/data/group/800319/junkData/temp_factor_by_fc/'

start_date = 20170101
end_date = 20191231
ref_days = 10
N = 1 # 前N日涨跌幅
index_code = 'ZZ500'

close = get_daily_1factor('close_badj')
close_pct_chg = close.pct_change(N).shift(1).loc[start_date:end_date]

bench_close = get_daily_1factor('close', code_list=[index_code], type='bench')
bench_close_pct_chg = bench_close.pct_change(N).shift(1).loc[start_date:end_date]
alpha = close_pct_chg.sub(bench_close_pct_chg.values, axis=0)

alpha_by_industry = pd.DataFrame(index=alpha.index)
for sw1_code in sw1_dict.keys():
    alpha_by_industry = pd.concat([alpha_by_industry, alpha[sw1_dict[sw1_code]].rank(pct=True)], axis=1)

print('开始进行回测')
factor = alpha_by_industry
fbt = FactorBackTest(group=10)
fbt.load_factor(factor)
fbt.calc_group_ret()
print(fbt.calc_ic().mean()) # 0.014497080367002022
fbt.report(factor=factor, address=root_path, file_name='junk_factor')

'''
N=1: 0.0145
N=2: 0.0095
N=3: 0.0053
N=4: -0.0024
N=5: 0.00022
N=10: 0.0011
'''