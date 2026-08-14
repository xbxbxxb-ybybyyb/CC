import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_20231026_8'
def factor_qyh_md_20231026_8(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close','pre_close','high'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                df_ori.reset_index()['dt'] >= '2020-08-24'))
                 | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    df_ori['bj'] = df_ori.reset_index()['Ticker'].apply(lambda x: x[-2:] == 'BJ').values
    df_ori['high_pct'] = df_ori['high']/df_ori['pre_close']-1#最高价对应的涨幅
    df_ori.loc[df_ori['zcz']==1,'high_pct'] = df_ori.loc[df_ori['zcz']==1,'high_pct']/2
    df_ori.loc[df_ori['bj']==1,'high_pct'] = df_ori.loc[df_ori['bj']==1,'high_pct']/3
    #
    df_ori['high_pct_filter'] = 0#最高价对应涨跌幅是否大于0.07
    df_ori.loc[df_ori['high_pct'] >= 0.05, 'high_pct_filter'] = 1
    #
    df_ori['high_filter'] = df_ori['high'] * df_ori['high_pct_filter']
    df_ori['high_filter_20'] = df_ori['high_filter'].unstack().rolling(20,5).max().stack()
    df_ori[factor_name] = df_ori['high_filter_20']/df_ori['close']
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
