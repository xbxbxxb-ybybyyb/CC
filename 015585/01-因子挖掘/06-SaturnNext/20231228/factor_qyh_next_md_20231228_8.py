import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# 开盘价/amt的T-1值除以20日标准差
# 25,0.056,0.04
#
factor_name = 'qyh_next_md_20231228_8'
def factor_qyh_next_md_20231228_8(start_date, end_date, IO, return_fillna_dic=False):
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
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt','open'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    # for col in ['vwap','pre_close','high','low','close']:
    #     df_ori[col] = df_ori[col] * df_ori['adjfactor']
    df_ori = df_ori[df_ori['amt'] > 0]
    df_ori = df_ori[df_ori['open'] > 0]
    df_ori['factor'] = df_ori['open'] / df_ori['amt']
    df_ori['factor'] = df_ori['factor'].apply(lambda x : round_(x,8))
    df_ori['factor1'] = ((df_ori['factor']).unstack().rolling(20,1).std().stack()+1e-5)
    df_ori['factor1'] = df_ori['factor1'].apply(lambda x : round_(x,8))
    df_ori[factor_name] = (df_ori['factor'])/ df_ori['factor1']
    df_ori[factor_name] = df_ori[factor_name].apply(lambda x : round_(x,6))
    # df_ori[factor_name] = df_ori[factor_name] - df_ori[factor_name].unstack().median(axis=1)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]