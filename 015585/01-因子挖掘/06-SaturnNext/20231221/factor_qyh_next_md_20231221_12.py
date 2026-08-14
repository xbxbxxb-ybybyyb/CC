import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# high/vwap的5日变化
# 24,-0.04,-0.03 score ok
#
factor_name = 'qyh_next_md_20231221_12'
def factor_qyh_next_md_20231221_12(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    import decimal
    def f_calc_change(factor_series):
        return factor_series[-1] - factor_series[0]
    start_date = int(s.tradingday(str(start_date), -180)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['pct_chg','high','low','vwap','close','adjfactor','amt','turn','pre_close'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    # df_ori['para'] = (df_ori['high'] - df_ori['low']).unstack().rolling(20,1).max().stack()
    # df_ori = df_ori[df_ori['para']>1e-5]
    # df_ori = df_ori[df_ori['amt']>1e-5]
    # for col in ['vwap','high']:
    #     df_ori[col] = df_ori[col] * df_ori['adjfactor']
    df_ori['factor'] = df_ori['high'] / df_ori['vwap']
    df_ori[factor_name] = df_ori['factor'].unstack().rolling(5,1).apply(lambda x : f_calc_change(x)).stack()
    #
    # df_ori['tmp'] = (df_ori['close'] - df_ori['pre_close'])/(df_ori['high'] + df_ori['low'])*2
    # df_ori['tmp'] = df_ori['tmp'].unstack().rolling(5,1).mean().stack()
    # #
    # df_ori.loc[df_ori['tmp'] < -0.0047,factor_name] = df_ori.loc[df_ori['tmp'] < -0.0047,factor_name] - 2*0.074
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]