import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_next_md_20231228_1'
def factor_qyh_next_md_20231228_1(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -180)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    for col in ['vwap','pre_close','high','low','close']:
        df_ori[col] = df_ori[col] * df_ori['adjfactor']
    df_ori[factor_name] = (df_ori['vwap']).unstack().rolling(5,1).min().stack() \
                          / df_ori['pre_close']
    df_ori[factor_name] = df_ori[factor_name] - df_ori[factor_name].unstack().median(axis=1)
    df_ori['A'] = (df_ori['low'] * df_ori['amt']).unstack().rolling(5,1).sum().stack() / (df_ori['amt'].unstack().rolling(5,1).sum().stack()+1)
    df_ori['B'] = (df_ori['close'] * df_ori['amt']).unstack().rolling(5, 1).sum().stack() / (
                df_ori['amt'].unstack().rolling(5, 1).sum().stack() + 1)
    df_ori['C'] = (df_ori['high']).unstack().rolling(20,1).median().stack() # high median
    df_ori['tmp2'] = (df_ori['A'] - df_ori['B']) / (df_ori['C'])
    df_ori.loc[df_ori['tmp2'] < -0.0967,factor_name] = df_ori.loc[df_ori['tmp2'] < -0.0967,factor_name] - 0.046*2
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]