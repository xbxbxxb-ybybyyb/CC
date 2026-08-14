# 每次修改第二行
from run_factor_demo_parallel_new import run_factor
import os
import pandas as pd
import numpy as np
'''
'''
factor_list = [
                'factor_qyh_ttick_risespeed_c'
]
#'factor_qyh_ttick_20231130_3','factor_qyh_ttick_b12b_tail_amt','factor_qyh_ttick_risespeed5','factor_qyh_ttick_risespeed_c'
for factor_name in factor_list:
    m = __import__(factor_name)
    func = getattr(m,factor_name)
    print(factor_name)
    basic_file_path = '/data/group/800463/data/project1_public/factor_lib_v3/Basic_zt_001_20150901_20191231.h5'
    result_path = '/data/user/015585/01-因子挖掘/03-Jupyter/20240513-历史因子修改leda/修改后/'
    if os.path.exists(result_path + factor_name + '.h5'):
        os.remove(result_path + factor_name + '.h5')
    factor_df0 = run_factor(func,
                            factor_name,
                            'TTickab',## TTickab,TOrder,TTransaction,T-1_factor,MarketIndTTick,TOrder_TTickab
                            20160101, 20191231,
                            basic_file_path,
                            result_path, interval_res=False)
