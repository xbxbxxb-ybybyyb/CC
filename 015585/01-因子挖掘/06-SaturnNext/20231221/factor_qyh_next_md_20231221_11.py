import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# abs(pct*turn)的50日集中度
# 30,-0.063,-0.048
#
factor_name = 'qyh_next_md_20231221_11'
def factor_qyh_next_md_20231221_11(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    def f_calc_sum(factor_series):
        return factor_series[~np.isnan(factor_series)].sum()

    def f_calc_cct(factor_series):
        if abs(f_calc_sum(factor_series)) > 0:
            return f_calc_sum(factor_series ** 2) / (f_calc_sum(factor_series) ** 2)
        else:
            return np.nan
    start_date = int(s.tradingday(str(start_date), -180)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['pct_chg','high','low','vwap','close','adjfactor','amt','turn','pre_close'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['para'] = (df_ori['high'] - df_ori['low']).unstack().rolling(20,1).max().stack()
    df_ori = df_ori[df_ori['para']>1e-5]
    df_ori = df_ori[df_ori['amt']>1e-5]
    # for col in ['vwap']:
    #     df_ori[col] = df_ori[col] * df_ori['adjfactor']
    df_ori['factor'] = abs(df_ori['pct_chg'] * df_ori['turn'])
    df_ori[factor_name] = df_ori['factor'].unstack().rolling(50,1).apply(lambda x : f_calc_cct(x)).stack()
    #
    df_ori['tmp1'] = (df_ori['close'] - df_ori['pre_close'])/(df_ori['high'] + df_ori['low'])*2
    df_ori['tmp1'] = df_ori['tmp1'].unstack().rolling(5,1).mean().stack()
    df_ori.loc[df_ori['tmp1'] < -0.0047,factor_name] = df_ori.loc[df_ori['tmp1'] < -0.0047,factor_name] - 0.074/2
    #
    df_ori['A'] = (df_ori['low'] * df_ori['amt']).unstack().rolling(5,1).sum().stack() / (df_ori['amt'].unstack().rolling(5,1).sum().stack()+1)
    df_ori['B'] = (df_ori['close'] * df_ori['amt']).unstack().rolling(5, 1).sum().stack() / (
                df_ori['amt'].unstack().rolling(5, 1).sum().stack() + 1)
    df_ori['C'] = (df_ori['high']).unstack().rolling(20,1).median().stack() # high median
    df_ori['tmp2'] = (df_ori['A'] - df_ori['B']) / (df_ori['C'])
    df_ori.loc[df_ori['tmp2'] < -0.0967,factor_name] = df_ori.loc[df_ori['tmp2'] < -0.0967,factor_name] + 2 * 0.074
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]