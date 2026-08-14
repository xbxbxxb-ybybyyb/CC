import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# 19,-0.059,-0.048
# 下影线的5日均值/60日均值
factor_name = 'qyh_sat_md_20240201_5'
def factor_qyh_sat_md_20240201_5(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['factor'] = (df_ori['close'] - df_ori['low']) / df_ori['pre_close']
    df_ori = df_ori[df_ori['amt'] > 0]
    # df_ori.loc[df_ori['zcz']==1,'factor'] = (df_ori.loc[df_ori['zcz']==1,'factor']-1) / 2 + 1
    df_ori[factor_name] = df_ori['factor'].unstack().rolling(5,1).mean().stack() / (df_ori['factor'].unstack().rolling(60,1).mean().stack()+1e-8)
    #
    # df_ori[factor_name] = df_ori[factor_name] - df_ori[factor_name].unstack().mean(axis=1)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]