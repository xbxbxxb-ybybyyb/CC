# 每次修改第二行
from run_factor_demo_parallel_new import run_factor
import os
import pandas as pd
import numpy as np

factor_name_list = os.listdir('/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/因子验证_ttick/factor/')
factor_name_list = [x.replace('.py','') for x in factor_name_list if '.py' in x and 'factor_' in x and 'run_factor' not in x]
factor_name_list.sort()
print(len(factor_name_list))
for factor_name in factor_name_list:
    # if factor_name != 'factor_1m_allbs_allp_allamt_all_alldf_calcbuybs_amt2buypctdiff_sum_minus':
    #     continue
    m = __import__(factor_name)
    func = getattr(m,factor_name)
    print(factor_name)

    start_date, end_date = 20170110, 20170110  # 因子的样本内区间：16-19年
    basic_file_path = '/data/user/015585/01-因子挖掘/20240624 xdb数据探索/file/basic_europa_20150930_20250710.h5'
    result_path = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/因子验证_ttick/factor_value_file/'
    if os.path.exists(result_path + factor_name + '.h5'):
        os.remove(result_path + factor_name + '.h5')
    factor_df0 = run_factor(func,
                            factor_name,
                            'TTickab',## TTickab,TOrder,TTransaction,T-1_factor,MarketIndTTick,TOrder_TTickab
                            start_date, end_date,
                            basic_file_path,
                            result_path, interval_res=False)
