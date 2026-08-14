import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# 下影线的5日离散程度/60日
# 25，0.063，0.062
#
factor_name = 'qyh_next_md_20231221_10'
def factor_qyh_next_md_20231221_10(start_date, end_date, IO, return_fillna_dic=False):
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

    def f_calc_m2m(factor_series):
        factor_series = factor_series[~np.isnan(factor_series)]
        return factor_series.max() / factor_series.mean() if factor_series.mean() > 0 else np.nan
    start_date = int(s.tradingday(str(start_date), -180)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['pct_chg','high','low','vwap','close','adjfactor','amt','pre_close'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['para'] = (df_ori['high'] - df_ori['low']).unstack().rolling(20,1).max().stack()
    df_ori = df_ori[df_ori['para']>1e-5]
    df_ori = df_ori[df_ori['amt']>1e-5]
    # for col in ['vwap']:
    #     df_ori[col] = df_ori[col] * df_ori['adjfactor']
    df_ori['factor'] = (df_ori['close'] - df_ori['low']) / df_ori['pre_close']
    df_ori[factor_name] = df_ori['factor'].unstack().rolling(5,1).apply(lambda x : f_calc_m2m(x)).stack() \
                          / df_ori['factor'].unstack().rolling(60,1).apply(lambda x : f_calc_m2m(x)).stack()
    # def rank_(data_):
    #     data_r = (data_.unstack().rank(axis=1) / (~ data_.unstack().isnull()).values.sum(axis=1).reshape(-1, 1)).stack()
    #     return data_r
    # df_ori[factor_name] = rank_(df_ori[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]