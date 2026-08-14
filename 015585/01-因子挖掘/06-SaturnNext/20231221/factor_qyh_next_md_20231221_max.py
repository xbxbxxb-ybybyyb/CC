import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# test
#
# < -0.0047
factor_name = 'qyh_next_md_20231221_7'
def factor_qyh_next_md_20231221_7(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    def f_calc_pos(factor_series):
        factor_series = factor_series[~np.isnan(factor_series)]
        return (factor_series[-1] - factor_series.min()) / \
               (factor_series.max() - factor_series.min() + 1e-8)
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
                          columns=['pct_chg','high','low','open','close','adjfactor','amt','pre_close','turn'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    # df_ori['para'] = (df_ori['high'] - df_ori['low']).unstack().rolling(20,1).max().stack()
    # df_ori = df_ori[df_ori['para']>1e-5]
    # df_ori = df_ori[df_ori['amt']>1e-5]
    # for col in ['open','high','low','close','pre_close']:
    #     df_ori[col] = df_ori[col] * df_ori['adjfactor']
    df_ori['factor'] = (df_ori['close'] - df_ori['pre_close'])/(df_ori['high'] + df_ori['low'])*2
    df_ori[factor_name] = df_ori['factor'].unstack().rolling(5,1).mean().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]