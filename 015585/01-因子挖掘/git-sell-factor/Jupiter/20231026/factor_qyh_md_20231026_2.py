import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_20231026_2'
def factor_qyh_md_20231026_2(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -30)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close','open','pre_close','high','low','amt'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['max_open_close'] = df_ori[['open', 'close']].max(axis=1)
    df_ori['min_open_close'] = df_ori[['open', 'close']].min(axis=1)
    df_ori['syx2'] = (df_ori['high'] - df_ori['max_open_close']) / df_ori['pre_close']
    df_ori['xyx2'] = (df_ori['min_open_close'] - df_ori['low']) / df_ori['pre_close']
    df_ori['factor'] = (df_ori['syx2'] - df_ori['xyx2']) * df_ori['amt']
    df_ori['factor'] = df_ori['factor'].unstack().rolling(5,1).max().stack()
    df_ori['amt_5_max'] = df_ori['amt'].unstack().rolling(5,1).max().stack()
    df_ori[factor_name] = df_ori['factor'] / (df_ori['amt_5_max']+1)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
