import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# pct * turn除以60日偏度
# 18，0.049，0.036
factor_name = 'qyh_sat_md_20240125_6'
def factor_qyh_sat_md_20240125_6(start_date, end_date, IO, return_fillna_dic=False):
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
    start_date = int(s.tradingday(str(start_date), -100)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt','pct_chg','turn'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['factor'] = df_ori.eval('pct_chg * turn').apply(lambda x : round_(x,10))
    df_ori = df_ori[df_ori['amt'] > 0]
    df_ori['skew'] = df_ori['factor'].unstack().rolling(60,1).skew().stack().apply(lambda x : round_(x,4)).replace(0,np.nan)
    df_ori[factor_name] = (df_ori['factor']) \
                          / df_ori['skew']
    df_ori[factor_name] = df_ori[factor_name].apply(lambda x :round_(x,2))
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]