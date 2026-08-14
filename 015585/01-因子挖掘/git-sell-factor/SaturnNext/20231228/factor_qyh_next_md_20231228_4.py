import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_next_md_20231228_4'
def factor_qyh_next_md_20231228_4(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0.075,'data':['MD']} # 0.029
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -50)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt','pct_chg'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['factor'] = (df_ori['close'] - df_ori['pre_close'])/(df_ori['high'] + df_ori['low'])*2
    df_ori[factor_name] = (df_ori['factor'] * df_ori['amt']).unstack().rolling(10,1).median().stack() \
                          / df_ori['amt'].unstack().rolling(10,1).median().stack()
    df_ori['A'] = (df_ori['low'] * df_ori['amt']).unstack().rolling(5,1).sum().stack() / (df_ori['amt'].unstack().rolling(5,1).sum().stack()+1)
    df_ori['B'] = (df_ori['close'] * df_ori['amt']).unstack().rolling(5, 1).sum().stack() / (
                df_ori['amt'].unstack().rolling(5, 1).sum().stack() + 1)
    df_ori['C'] = (df_ori['high']).unstack().rolling(20,1).median().stack() # high median
    df_ori['tmp2'] = (df_ori['A'] - df_ori['B']) / (df_ori['C'])
    df_ori.loc[df_ori['tmp2'] < -0.0967,factor_name] = df_ori.loc[df_ori['tmp2'] < -0.0967,factor_name] + 0.0056*3
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]