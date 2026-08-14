import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# 下影线用amt的倒数修正的5日和
# 41，0.077，0.071
factor_name = 'qyh_sat_md_20240229_5'
def factor_qyh_sat_md_20240229_5(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','pct_chg','close','high','low','amt','open'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['syx1'] = (df_ori['high'] - df_ori['close']) / df_ori['close']
    df_ori['factor'] = df_ori['syx1'] / (df_ori['amt'])
    df_ori = df_ori[df_ori['amt'] > 1]
    df_ori[factor_name] = df_ori['factor'].unstack().rolling(5,1).sum().stack() * (df_ori['amt'].unstack().rolling(5,1).sum().stack()+1)
    # df_ori[factor_name] = df_ori[factor_name] - df_ori[factor_name].unstack().median(axis=1)
    # df_ori[factor_name] = df_ori[factor_name].apply(lambda x : round_(x,5))
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]