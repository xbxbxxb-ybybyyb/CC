import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# 昨日涨跌幅/60日最低价和t-1最高价的差距
# 22，-0.065，-0.082
# xbj!!!!!
factor_name = 'qyh_next_md_20231228_10'
def factor_qyh_next_md_20231228_10(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -180)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori[factor_name] = (df_ori['close'] / df_ori['pre_close']) / (df_ori['close'].unstack().rolling(60,1).min().stack() / df_ori['high'])
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]