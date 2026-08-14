import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_zyyx_20231228_1'
'''
直接选取europa样本池中：
1）研报中披露超预期
2）未披露
观察该标识有无影响
'''
def factor_qyh_zyyx_20231228_1(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    df_ori = pd.read_pickle('/data/user/015585/01-因子挖掘/20231212_zyyx/file/is_beyond_est.pkl')
    df_ori[factor_name] = df_ori['is_beyond_est']
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
