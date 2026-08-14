import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_sat_md_20240104_5'
def factor_qyh_sat_md_20240104_5(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['factor'] = df_ori['close'] / df_ori['vwap']
    df_ori['para'] = (df_ori['high'] - df_ori['low']).unstack().rolling(5,1).max().stack()
    df_ori['std'] = df_ori['factor'].unstack().rolling(5,1).std().stack()
    df_ori.loc[df_ori['para'] < 1e-4,'std'] = 0
    df_ori[factor_name] = df_ori['factor'].unstack().rolling(5,1).mean().stack() / (df_ori['std'] +1e-2)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]