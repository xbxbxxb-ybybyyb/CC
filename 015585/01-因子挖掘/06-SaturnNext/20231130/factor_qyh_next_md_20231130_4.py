import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_next_md_20231130_4'
# dtj
# (high+low)20日均值 / close 20日均值
# 36,-0.09
def factor_qyh_next_md_20231130_4(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close','pre_close','high','vwap','low','open','amt'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    # df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
    #             df_ori.reset_index()['dt'] >= '2020-08-24'))
    #              | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    #
    df_ori['A'] = df_ori['close'].unstack().rolling(20,1).mean().stack()
    df_ori['C'] = 0.5*(df_ori['high'] + df_ori['low']).unstack().rolling(20,1).mean().stack()
    df_ori[factor_name] = (df_ori['A']) / df_ori['C']
    # df_ori[factor_name] = df_ori[factor_name].unstack().rolling(20,1).mean().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
