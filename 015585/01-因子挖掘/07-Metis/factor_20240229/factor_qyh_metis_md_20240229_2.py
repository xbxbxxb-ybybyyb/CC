import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# T-1下影线/60日集中度
# 21，-0.039，-0.036
factor_name = 'qyh_metis_md_20240229_2'
def factor_qyh_metis_md_20240229_2(start_date, end_date, IO, return_fillna_dic=False):
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

    def f_calc_sum(factor_series):
        return factor_series[~np.isnan(factor_series)].sum()

    def f_calc_cct(factor_series):
        if abs(f_calc_sum(factor_series)) > 0:
            return f_calc_sum(factor_series ** 2) / (f_calc_sum(factor_series) ** 2)
        else:
            return np.nan
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['pre_close','close','open','amt','pct_chg','vwap','low'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['factor'] = (df_ori['close'] - df_ori['low']) / df_ori['pre_close']
    df_ori = df_ori[df_ori['amt']>1]
    df_ori[factor_name] = df_ori['factor']/ df_ori['factor'].unstack().rolling(20,1).apply(lambda x : f_calc_cct(x)).stack()
    # df_ori[factor_name] = df_ori[factor_name].apply(lambda x : round_(x,5))
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]