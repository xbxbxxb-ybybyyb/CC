import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_next_md_20231130_1'
def factor_qyh_next_md_20231130_1(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close','pre_close','high','vwap','low','open'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['A'] = df_ori['high'].unstack().rolling(20,1).mean().stack()
    df_ori['B'] = df_ori['close'].unstack().fillna(method='ffill',limit=20).stack()
    df_ori['C'] = (df_ori['low']).unstack().fillna(method='ffill',limit=20).stack()
    df_ori[factor_name] = (df_ori['A'] - df_ori['B']) / (df_ori['C'])
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
