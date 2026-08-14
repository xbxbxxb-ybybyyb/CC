import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_next_md_20231228_14'
def factor_qyh_next_md_20231228_14(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    start_date = int(s.tradingday(str(start_date), -180)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    x = 'amt'
    y = 'xyx1'
    df_ori = df_ori[df_ori['amt'] > 0]
    df_ori = df_ori[df_ori['pre_close'] > 0]
    df_ori[y] = ((df_ori['close'] - df_ori['low']) / df_ori['pre_close']).apply(lambda x : round_(x,10))
    df_ori['xy'] = (df_ori[x] * df_ori[y]).apply(lambda x : round_(x,10))
    df_ori['exy'] = (df_ori['xy'].unstack().rolling(20,5).mean().stack()).apply(lambda x : round_(x,8))
    df_ori['ex'] = (df_ori[x].unstack().rolling(20,5).mean().stack()).apply(lambda x : round_(x,10))
    df_ori['ey'] = (df_ori[y].unstack().rolling(20,5).mean().stack()).apply(lambda x : round_(x,10))
    df_ori['stdx'] = (df_ori[x].unstack().rolling(20,5).std().stack()).apply(lambda x : round_(x,8))
    df_ori['stdy'] = (df_ori[y].unstack().rolling(20,5).std().stack()).apply(lambda x : round_(x,8))
    df_ori = df_ori[df_ori['stdx'] > 1e-6]
    df_ori = df_ori[df_ori['stdy'] > 1e-6]
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey']).apply(lambda x : round_(x,6))\
                       /(df_ori['stdx'] * df_ori['stdy']).apply(lambda x : round_(x,6))
    df_ori[factor_name] = df_ori['factor'].apply(lambda x: 1 if x > 1.0001 else -1 if x < -1.0001 else x)
    df_ori[factor_name] = df_ori[factor_name].apply(lambda x : round_(x,5))
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]