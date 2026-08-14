import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# 均价5日均值/10日均值的rank
# 18，-0.047
# -0.052
factor_name = 'qyh_next_md_20231221_9'
def factor_qyh_next_md_20231221_9(start_date, end_date, IO, return_fillna_dic=False):
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
                          columns=['pct_chg','high','low','vwap','adjfactor'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['para'] = (df_ori['high'] - df_ori['low']).unstack().rolling(20,1).max().stack()
    df_ori = df_ori[df_ori['para']>1e-5]
    df_ori = df_ori[df_ori['vwap']>1e-5]
    for col in ['vwap']:
        df_ori[col] = df_ori[col] * df_ori['adjfactor']
    df_ori['up'] = np.sign(df_ori['pct_chg'])
    df_ori['up'] = df_ori['up'].apply(lambda x : 1 if x >= 0.5 else np.nan)
    df_ori['factor'] = df_ori['vwap'] * df_ori['up']
    df_ori[factor_name] = df_ori['factor'].unstack().rolling(5,1).mean().stack().apply(lambda x : round_(x,8))  / (df_ori['factor'].unstack().rolling(10,1).mean().stack().apply(lambda x : round_(x,8))+1e-8)
    df_ori[factor_name] = df_ori[factor_name].apply(lambda x : round_(x,6))
    def rank_(data_):
        data_r = (data_.unstack().rank(axis=1) / (~ data_.unstack().isnull()).values.sum(axis=1).reshape(-1, 1)).stack()
        return data_r
    df_ori[factor_name] = rank_(df_ori[factor_name]).apply(lambda x : round_(x,4))
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]