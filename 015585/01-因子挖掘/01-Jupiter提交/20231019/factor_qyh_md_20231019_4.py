import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_20231019_4'
def factor_qyh_md_20231019_4(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -30)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close','open','pre_close','high','low'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['syx1'] = (df_ori['high'] - df_ori['close']) / df_ori['pre_close']
    df_ori['xyx1'] = (df_ori['close'] - df_ori['low']) / df_ori['pre_close']
    df_ori['factor'] = (df_ori['syx1'] / df_ori['xyx1'].apply(lambda x : 0.001 if abs(x) <=0.001 else x))
    df_ori['factor2'] = (df_ori['factor'].unstack().rolling(20,1).min().stack())\
        .apply(lambda x:0.001 if abs(x) <=0.001 else x)
    df_ori[factor_name] = (df_ori['factor']) / (df_ori['factor2'])
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
