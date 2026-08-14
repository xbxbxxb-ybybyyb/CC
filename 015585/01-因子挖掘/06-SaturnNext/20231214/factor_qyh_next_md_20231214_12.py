import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# vwap 20日偏度
# -0.06,27
#
factor_name = 'qyh_next_md_20231214_12'
def factor_qyh_next_md_20231214_12(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
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
                          columns=['vwap','adjfactor','high','low'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['vwap'] = df_ori['vwap'] * df_ori['adjfactor']
    df_ori['vwap'] = df_ori['vwap'].unstack().fillna(method='ffill',limit=20).stack()
    df_ori['para'] = (df_ori['high'] - df_ori['low']).unstack().rolling(20,1).max().stack()
    df_ori[factor_name] = df_ori['vwap'].unstack().rolling(20,1).skew().stack()
    df_ori = df_ori[df_ori['para']>1e-5]
    df_ori[factor_name] = df_ori[factor_name].apply(lambda x : round_(x,4))
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]