import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_next_md_20231221_3'
def factor_qyh_next_md_20231221_3(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -180)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['pct_chg','high','low','open','close','adjfactor','amt','pre_close'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['para'] = (df_ori['high'] - df_ori['low']).unstack().rolling(20,1).max().stack()
    df_ori = df_ori[df_ori['para']>1e-5]
    df_ori = df_ori[df_ori['amt']>1e-5]
    for col in ['open','high','low','close','pre_close']:
        df_ori[col] = df_ori[col] * df_ori['adjfactor']
    df_ori['max_open_close'] = df_ori[['open', 'close']].max(axis=1)
    df_ori['min_open_close'] = df_ori[['open', 'close']].min(axis=1)
    df_ori['syx2'] = (df_ori['high'] - df_ori['max_open_close']) / df_ori['pre_close']
    df_ori['xyx2'] = (df_ori['min_open_close'] - df_ori['low']) / df_ori['pre_close']
    df_ori['factor'] = (df_ori['syx2'] - df_ori['xyx2'])*df_ori['amt']
    df_ori[factor_name] = df_ori['factor'].unstack().rolling(5,1).min().stack() / df_ori['amt'].unstack().rolling(5,1).min().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]