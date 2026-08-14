import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_20231109_2'
# zcz,dtj
# abs(pct*turn)的60日峰度
# 32,-0.06
#
def factor_qyh_md_20231109_2(start_date, end_date, IO, return_fillna_dic=False):
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
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['pct_chg','turn','pre_close','amt','vwap'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                df_ori.reset_index()['dt'] >= '2020-08-24'))
                 | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    df_ori['factor'] = df_ori['pct_chg']
    df_ori.loc[df_ori['zcz'] == 1, 'factor'] = df_ori.loc[df_ori['zcz'] == 1, 'factor']/2
    df_ori['factor'] = abs(df_ori['factor'] * df_ori['turn'])
    df_ori['test'] = abs(df_ori['factor']).unstack().rolling(60,5).mean().stack()
    df_ori[factor_name] = df_ori['factor'].unstack().rolling(60,5).kurt().stack()
    df_ori[factor_name] = df_ori[factor_name].apply(lambda x : np.log(x)+32 if x > 32 \
    else -np.log(-x)-1 if x < -1 else x)
    df_ori[factor_name] = df_ori[factor_name].apply(lambda x : round_(x,4))
    df_ori.loc[df_ori['test']<=1e-5,factor_name] = np.nan
    # -------------------------------------------------------------------------------------------------------------------
#     return df_ori
    return df_ori[[factor_name]]