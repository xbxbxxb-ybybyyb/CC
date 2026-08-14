import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# 北向资金：近20日持仓量变化，缺失值直接用中位数填充
'''
接近60%都要用填充值
用中位数填充后，IC极弱，0.01
'''
#
factor_name = 'qyh_md_20231130_test1'
def factor_qyh_md_20231130_test1(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    df_ori = pd.read_pickle('/data/user/015585/01-因子挖掘/20231128_北向资金/file/north_funds.pkl')
    df_ori['qty'] = df_ori['qty'].unstack().fillna(method = 'ffill',limit = 20).stack()
    df_ori[factor_name] = df_ori['qty'] / df_ori['qty'].unstack().shift(20).stack() - 1
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
