import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_next_md_20231228_12'
def factor_qyh_next_md_20231228_12(start_date, end_date, IO, return_fillna_dic=False):
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
    df_ori = df_ori[df_ori['vwap'] > 0]
    df_ori['factor'] = (df_ori['close'] - df_ori['pre_close'])/(df_ori['vwap'])
    df_ori['factor'] = df_ori['factor'].apply(lambda x : round_(x,9))
    df_ori[factor_name] = (df_ori['factor']).unstack().rolling(5,1).skew().stack()
    df_ori[factor_name] = df_ori[factor_name].apply(lambda x : round_(x,6))
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]