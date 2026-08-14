import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# T-1日最低价对应涨跌幅/5日离散程度的超额值
# 24，-0.056，-0.052
factor_name = 'qyh_sat_md_20240111_10'
def factor_qyh_sat_md_20240111_10(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    def f_calc_m2m(factor_series):
        factor_series = factor_series[~np.isnan(factor_series)]
        return factor_series.max() / factor_series.mean() if factor_series.mean() > 0 else np.nan
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt','pct_chg'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['factor'] = (df_ori['low']) / df_ori['pre_close']
    df_ori[factor_name] = df_ori['factor'] \
                          / (df_ori['factor'].unstack().rolling(5,1).apply(lambda x : f_calc_m2m(x)).stack())
    df_ori[factor_name] = df_ori[factor_name] - df_ori[factor_name].unstack().median(axis=1)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]