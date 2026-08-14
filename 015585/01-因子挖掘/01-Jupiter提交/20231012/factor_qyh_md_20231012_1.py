import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_20231012_1'
def factor_qyh_md_20231012_1(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -30)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close','high','pre_close','low'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                df_ori.reset_index()['dt'] >= '2020-08-24'))
                 | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    df_ori['factor'] = (df_ori['high'] - df_ori['close']) / (df_ori['high'] - df_ori['low'])
    df_ori.loc[df_ori['zcz'] == 1, 'factor'] = df_ori.loc[df_ori['zcz'] == 1, 'factor']/2
    df_ori[factor_name] = df_ori['factor'].unstack().rolling(5,1).mean().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
