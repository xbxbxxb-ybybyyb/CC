import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_perform_120'
# 120日内，股价收盘首次涨停的话，平均次日开盘涨幅
# open/close/rank/触板
#
def factor_qyh_md_perform_120(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.48,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -600)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close','adjfactor','open','high'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['close'] = df_ori['close'] * df_ori['adjfactor']
    df_ori['open'] = df_ori['open'] * df_ori['adjfactor']
    df_ori['high'] = df_ori['high'] * df_ori['adjfactor']
    #
    df_ori['pre_close'] = df_ori['close'].unstack().shift(1).stack()
    df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                df_ori.reset_index()['dt'] >= '2020-08-24'))
                 | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    zt_price = np.floor(df_ori['pre_close'] * 100 * 1.1+0.5)/100
    zt_price[df_ori['zcz']] = np.floor(df_ori['pre_close'] * 100 * 1.2+0.5)/100
    df_ori['p_zt'] = zt_price
    df_ori['is_zt'] = df_ori['high'] >= df_ori['p_zt']
    df_ori['is_pre_zt'] = df_ori['is_zt'].unstack().shift(1).stack()
    df_ori['is_first_zt'] = np.floor((df_ori['is_zt'] == 1) & (df_ori['is_pre_zt'] == 0))
    df_ori['next_open'] = df_ori['open'].unstack().shift(-1).stack()
    #
    df_ori['next_open_pct'] = df_ori['next_open'] / df_ori['high'] - 1
    df_ori.loc[df_ori['zcz']==1,'next_open_pct'] = df_ori.loc[df_ori['zcz']==1,'next_open_pct']/2
    df_ori['next_open_pct_zt'] = df_ori['next_open_pct'] * df_ori['is_first_zt']
    df_ori['next_open_pct_zt'].replace(0, np.nan,inplace = True)
    df_ori[factor_name] = df_ori['next_open_pct_zt'].unstack().rolling(500,1).mean().stack()
    df_ori[factor_name] = df_ori[factor_name].unstack().rank(axis=1).stack() / df_ori['close'].unstack().count(axis=1)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
