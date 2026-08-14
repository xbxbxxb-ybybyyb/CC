import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# 13,0.058,0.056
# T-1成交量/60日偏度
factor_name = 'qyh_sat_md_20240229_4'
def factor_qyh_sat_md_20240229_4(start_date, end_date, IO, return_fillna_dic=False):
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

    def f_calc_kurt(factor_series):
        factor_series = factor_series[~np.isnan(factor_series)]
        mean = factor_series.mean()
        std = factor_series.std(ddof=1)
        n = len(factor_series)
        if n < 4:
            return np.nan
        else:
            kurt = sum(((factor_series - mean) / std) ** 4)
            kurt = kurt * n * (n + 1) / (n - 1) / (n - 2) / (n - 3) - 3 * (n - 1) * (n - 1) / (n - 2) / (n - 3)
            return kurt
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['factor'] = df_ori['amt']
    df_ori[factor_name] = df_ori['factor'] / df_ori['factor'].unstack().rolling(60,1).apply(lambda x : f_calc_kurt(x)).stack()
    # df_ori[factor_name] = df_ori[factor_name].apply(lambda x : round_(x,5))
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]