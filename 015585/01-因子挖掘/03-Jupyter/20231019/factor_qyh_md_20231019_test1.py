import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_20231019_test1'
#
# 定义回调的反弹：最近20交易日出现过2次以上涨停 & 目前相对20日最高价回撤超过20%
#
#
def factor_qyh_md_20231019_test1(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.5,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -30)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close','open','pre_close','high','adjfactor'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                df_ori.reset_index()['dt'] >= '2020-08-24'))
                 | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    df_ori['close'] = df_ori['close'] * df_ori['adjfactor']
    df_ori['pre_close'] = df_ori['pre_close'] * df_ori['adjfactor']
    df_ori['p_zt'] = np.floor(df_ori['pre_close'] * 100 * 1.1 + 0.5) / 100
    df_ori.loc[df_ori['zcz']==1,'p_zt'] = \
        np.floor(df_ori.loc[df_ori['zcz']==1,'pre_close'] * 100 * 1.2 + 0.5) / 100
    df_ori['is_zt'] = (df_ori['close'] >= df_ori['p_zt'])
    df_ori['con1'] = df_ori['is_zt'].unstack().rolling(20,5).sum().stack()
    df_ori['max20'] = df_ori['close'].unstack().rolling(20,5).max().stack()
    df_ori['con2'] = 1-df_ori['close'] / df_ori['max20']
    df_ori[factor_name] = ((df_ori['con1'] >= 2) & (df_ori['con2'] >=0.1)).apply(lambda x:int(x))
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
