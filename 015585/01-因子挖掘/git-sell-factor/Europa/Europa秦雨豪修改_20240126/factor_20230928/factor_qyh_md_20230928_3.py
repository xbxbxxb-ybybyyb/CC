import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_20230928_3'
def factor_qyh_md_20230928_3(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -30)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close','high','pre_close','open','low','amt'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                df_ori.reset_index()['dt'] >= '2020-08-24'))
                 | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    # df_ori['new1'] = df_ori[['close','open']].max(axis=1)
    # df_ori['new2'] = df_ori[['close','open']].min(axis=1)
    df_ori['syx1'] = (df_ori['high'] - df_ori['close']) / df_ori['pre_close']
    df_ori['xyx1'] = (df_ori['close'] - df_ori['low']) / df_ori['pre_close']
    df_ori['factor'] = (df_ori['syx1'] - df_ori['xyx1'])
    df_ori.loc[df_ori['zcz'] == 1, 'factor'] = df_ori.loc[df_ori['zcz'] == 1, 'factor']/2
    df_ori['factor'] = df_ori['factor'] * df_ori['amt']
    df_ori['res1'] = df_ori['factor'].unstack().rolling(5,1).sum().stack()
    df_ori['res2'] = df_ori['amt'].unstack().rolling(5,1).sum().stack()
    df_ori['res2'] = df_ori['res2'].apply(lambda x : 1 if abs(x)<1 else x)
    df_ori[factor_name] = df_ori['res1']/df_ori['res2']
    # df_ori[factor_name] = df_ori[factor_name].unstack().rank(axis=1).stack().div(df_ori['close'].unstack().count(axis=1))
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
