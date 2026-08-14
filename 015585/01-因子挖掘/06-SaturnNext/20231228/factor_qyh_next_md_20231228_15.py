import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# 涨跌幅绝对值的5日离散程度和22日比对
# 20，0.049，0.031
#
factor_name = 'qyh_next_md_20231228_15'
def factor_qyh_next_md_20231228_15(start_date, end_date, IO, return_fillna_dic=False):
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
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt','pct_chg'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    # for col in ['vwap','pre_close','high','low','close']:
    #     df_ori[col] = df_ori[col] * df_ori['adjfactor']
    # df_ori = df_ori[df_ori['amt'] > 0]
    df_ori['factor'] = abs(df_ori['pct_chg'])
    df_ori['up'] = np.sign(df_ori['pct_chg'])
    df_ori['up'] = df_ori['up'].apply(lambda x : 1 if x >= 0.5 else np.nan)
    df_ori['factor'] = df_ori['factor'] * df_ori['up']
    df_ori[factor_name] = (df_ori['factor'].unstack().rolling(5,1).apply(lambda x :f_calc_cct(x)).stack()) \
                          / ((df_ori['factor']).unstack().rolling(22,1).apply(lambda x :f_calc_cct(x)).stack())
    #
    # df_ori[factor_name] = df_ori[factor_name] - df_ori[factor_name].unstack().median(axis=1)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]