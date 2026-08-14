import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# 最高价对应涨跌幅的5日amt加权平均
# 28=7.95，-0.079，-0.085
# zwh_20231207_013：19
factor_name = 'qyh_next_md_20231228_3'
def factor_qyh_next_md_20231228_3(start_date, end_date, IO, return_fillna_dic=False):
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
    df_ori = df_ori[df_ori['amt'] > 0]
    df_ori['factor'] = df_ori['high'] / df_ori['pre_close']
    df_ori[factor_name] = (df_ori['factor'] * df_ori['amt']).unstack().rolling(5,1).mean().stack() \
                          / (df_ori['amt']).unstack().rolling(5,1).mean().stack()
    #
    # df_ori[factor_name] = df_ori[factor_name] - df_ori[factor_name].unstack().median(axis=1)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]