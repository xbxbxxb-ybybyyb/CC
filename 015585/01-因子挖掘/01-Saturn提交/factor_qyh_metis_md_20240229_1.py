import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# close/vwap根据amt修正的5日均值
# 30，-0.049，-0.044
factor_name = 'qyh_metis_md_20240229_1'
def factor_qyh_metis_md_20240229_1(start_date, end_date, IO, return_fillna_dic=False):
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
                          columns=['pre_close','close','open','amt','pct_chg','vwap'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['factor'] = df_ori['close'] / df_ori['vwap'] * df_ori['amt']
    df_ori = df_ori[df_ori['amt']>1]
    df_ori[factor_name] = df_ori['factor'].unstack().rolling(5,1).mean().stack() / df_ori['amt'].unstack().rolling(5,1).mean().stack()
    # df_ori[factor_name] = df_ori[factor_name].apply(lambda x : round_(x,5))
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]