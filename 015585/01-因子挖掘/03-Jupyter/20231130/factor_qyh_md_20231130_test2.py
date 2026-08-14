import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# 北向资金：近20日持仓量变化，取每日持仓变化的20日平均，缺失值直接用中位数填充
'''

'''
#
factor_name = 'qyh_md_20231130_test2'
def factor_qyh_md_20231130_test2(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    df_ori = pd.read_pickle('/data/user/015585/01-因子挖掘/20231128_北向资金/file/north_funds.pkl')
    # df_ori['qty'] = df_ori['qty'].unstack().fillna(method = 'ffill',limit = 20).stack()
    df_ori['qty_delta'] = df_ori['qty'] / df_ori['qty'].unstack().shift(1).stack() - 1
    para = 5
    df_ori[factor_name] = df_ori['qty_delta'].unstack().rolling(para,5).mean().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
