import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_20231109_3'
# zcz,dtj
# 涨跌幅 * 换手率的上涨部分的60日偏度
# 42,-0.068,-0.07
#
def factor_qyh_md_20231109_3(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:2.31,'data':['MD']}
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
    df_ori['bj'] = df_ori.reset_index()['Ticker'].apply(lambda x: x[-2:] == 'BJ').values
    df_ori['factor'] = df_ori['pct_chg']
    df_ori.loc[df_ori['zcz'] == 1, 'factor'] = df_ori.loc[df_ori['zcz'] == 1, 'factor']/2
    df_ori.loc[df_ori['bj'] == 1, 'factor'] = df_ori.loc[df_ori['bj'] == 1, 'factor']/3
    df_ori['factor'] = df_ori['factor'] * df_ori['turn']
    df_ori['up'] = np.sign(df_ori['pct_chg'])
    df_ori['up'] = df_ori['up'].apply(lambda x : 1 if x >= 0.5 else np.nan)
    df_ori['factor'] = df_ori['factor'] * df_ori['up']
    df_ori[factor_name] = df_ori['factor'].unstack().rolling(60,5).skew().stack()
    df_ori[factor_name] = df_ori[factor_name].apply(lambda x : round_(x,2)) # 矩阵大小不同时，Python精度差异，导致计算值不同
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
