import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# 19,-0.059,-0.048
# 下影线的5日均值/60日均值
factor_name = 'qyh_sat_md_20240222_1'
def factor_qyh_sat_md_20240222_1(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    import decimal
    def round_(x, n=0):
        x = x + 1e-10
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['factor'] = (df_ori['close'] - df_ori['low']) / df_ori['pre_close']
    df_ori = df_ori[df_ori['amt'] > 1]
    df_ori['tmp'] = df_ori['factor'].unstack().rolling(60,1).mean().stack()
    df_ori['tmp'] = df_ori['tmp'].apply(lambda x :round_(x,7))
    df_ori = df_ori[df_ori['tmp'] > 1e-5]
    df_ori[factor_name] = df_ori['factor'].unstack().rolling(5,1).mean().stack() / (df_ori['tmp'])
    df_ori[factor_name] = df_ori[factor_name].apply(lambda x : round_(x,5))
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]