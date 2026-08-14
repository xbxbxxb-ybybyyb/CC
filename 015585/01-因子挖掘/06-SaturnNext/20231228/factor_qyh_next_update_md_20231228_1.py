import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# 涨跌幅绝对值的5日均值 - 60日均值
# 19,-0.059,-0.058
#
factor_name = 'qyh_next_update_md_20231228_1'
def factor_qyh_next_update_md_20231228_1(start_date, end_date, IO, return_fillna_dic=False):
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
                          columns=['pct_chg','high','low'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['para'] = (df_ori['high'] - df_ori['low']).unstack().rolling(20,1).max().stack()
    df_ori[factor_name] = abs(df_ori['pct_chg']).unstack().rolling(5,1).mean().stack().apply(lambda x :round_(x,8)) \
                         - abs(df_ori['pct_chg']).unstack().rolling(60,1).mean().stack().apply(lambda x :round_(x,8))
    df_ori = df_ori[df_ori['para']>1e-5]
    df_ori[factor_name] = df_ori[factor_name].apply(lambda x : round_(x,4))
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]