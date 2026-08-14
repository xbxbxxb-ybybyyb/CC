import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# T-1vwap涨跌幅和60日最小vwap的比例
# 20，-0.058，-0.073
#
factor_name = 'qyh_next_md_20231228_11'
def factor_qyh_next_md_20231228_11(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -180)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    # for col in ['vwap','pre_close','high','low','close']:
    #     df_ori[col] = df_ori[col] * df_ori['adjfactor']
    # df_ori['factor'] =
    df_ori[factor_name] = (df_ori['vwap'] / df_ori['pre_close']) \
                          / (df_ori['vwap'].unstack().rolling(60,1).min().stack() / df_ori['pre_close'])
    #
    # df_ori[factor_name] = df_ori[factor_name] - df_ori[factor_name].unstack().mean(axis=1)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]