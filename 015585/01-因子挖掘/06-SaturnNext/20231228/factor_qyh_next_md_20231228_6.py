import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# 20日量价相关性的5日最大值
# -0.055，-0.063，24
# sss_corrct_20：25
factor_name = 'qyh_next_md_20231228_6'
def factor_qyh_next_md_20231228_6(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0.92,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------

    start_date = int(s.tradingday(str(start_date), -180)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    x = 'amt'
    y = 'close'
    para = 20
    df_ori = df_ori[df_ori['amt'] > 0]
    df_ori = df_ori[df_ori['low'] > 0]
    df_ori['xy'] = df_ori[x] * df_ori[y]
    df_ori['exy'] = df_ori['xy'].unstack().rolling(para,5).mean().stack()
    df_ori['ex'] = df_ori[x].unstack().rolling(para,5).mean().stack()
    df_ori['ey'] = df_ori[y].unstack().rolling(para,5).mean().stack()
    df_ori['stdx'] = df_ori[x].unstack().rolling(para,5).std().stack()
    df_ori['stdy'] = df_ori[y].unstack().rolling(para,5).std().stack()
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey'])\
                       /(df_ori['stdx'] * df_ori['stdy'])
    df_ori['factor'] = df_ori['factor'].apply(lambda x : 1 if x > 1.0001 else -1 if x < -1.0001 else x)
    df_ori['factor'] = df_ori['factor'].apply(lambda x : round_(x,8))
    df_ori[factor_name] = (df_ori['factor']).unstack().rolling(5,1).max().stack()
    df_ori[factor_name] = df_ori[factor_name].apply(lambda x : round_(x,6))
    #
    # df_ori[factor_name] = df_ori[factor_name] - df_ori[factor_name].unstack().median(axis=1)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]