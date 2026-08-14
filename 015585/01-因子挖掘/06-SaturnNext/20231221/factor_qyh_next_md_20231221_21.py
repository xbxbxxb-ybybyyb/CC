import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# 振幅的20日均值，amt加权，叠加影线处理
# 28，-0.062，-0.07
# skk_cc2l_std_a：15
factor_name = 'qyh_next_md_20231221_21'
def factor_qyh_next_md_20231221_21(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    def f_calc_change(factor_series):
        return factor_series[-1] - factor_series[0]
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
                          columns=['amt','high','low','pre_close','close'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['factor'] = (df_ori['high'] - df_ori['low']) / df_ori['pre_close']
    df_ori[factor_name] = (df_ori['factor'] * df_ori['amt']).unstack().rolling(20,1).mean().stack() / df_ori['amt'].unstack().rolling(20,1).mean().stack()
    # df_ori[factor_name] = df_ori[factor_name] - df_ori[factor_name].unstack().median(axis=1)
    # df_ori[factor_name] = df_ori[factor_name].apply(lambda x : round_(x,5))
    #
    df_ori['tmp'] = (df_ori['close'] - df_ori['pre_close'])/(df_ori['high'] + df_ori['low'])*2
    df_ori['tmp'] = df_ori['tmp'].unstack().rolling(5,1).mean().stack()
    df_ori.loc[df_ori['tmp'] < -0.0047,factor_name] = df_ori.loc[df_ori['tmp'] < -0.0047,factor_name] - 0.017*2

    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]