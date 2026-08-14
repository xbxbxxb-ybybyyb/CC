# 每次修改第二行
from run_factor_demo_parallel_new import run_factor
import os
from test_factor_demo import strongFactorTest
# from StrongFactorTest import StrongFactorTest
import pandas as pd
import numpy as np
'''
'''
date = '20991231'#周四日期
factor_list = list(os.listdir('/data/user/015585/01-因子挖掘/03-Jupyter/20991231/'))
factor_list = [x.replace('.py','') for x in factor_list if '.py' in x and 'md' in x]
factor_list.sort()
for factor_name in factor_list[50:]:
    result_path = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20250530_zwhmd_filter/'
    if os.path.exists(result_path + factor_name + '.h5'):
        continue

    m = __import__(factor_name)
    func = getattr(m,factor_name)
    print(factor_name)
    start_date, end_date = 20170101, 20250630  # 因子的样本内区间：16-19年
    basic_file_path = '/data/user/015585/01-因子挖掘/20240624 run/file/basic_europa_20150930_20250710.h5'
    factor_df0 = run_factor(func,
                            factor_name,
                            'T-1_factor',## TTickab,TOrder,TTransaction,T-1_factor,MarketIndTTick,TOrder_TTickab
                            start_date, end_date,
                            basic_file_path,
                            result_path, interval_res=False)
