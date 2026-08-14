import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# 38,-0.054
# close/vwap的T-1值，除以5日变异系数
factor_name = 'qyh_sat_md_20240111_9'
def factor_qyh_sat_md_20240111_9(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    def f_calc_avg(factor_series):
        return factor_series[~np.isnan(factor_series)].mean()
    def f_calc_cv(factor_series):
        if abs(f_calc_avg(factor_series)) > 0:
            return np.std(factor_series[~np.isnan(factor_series)], ddof=1) / f_calc_avg(factor_series)
        else:
            return np.nan
    def rank_(data_):
        data_r = (data_.unstack().rank(axis=1) / (~ data_.unstack().isnull()).values.sum(axis=1).reshape(-1, 1)).stack()
        return data_r
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt','pct_chg'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['factor'] = df_ori['close'] / df_ori['vwap']
    df_ori = df_ori[df_ori['factor'] > 0]
    df_ori['para'] = df_ori['factor'].unstack().rolling(5,1).apply(lambda x : x.max() - x.min()).stack()
    df_ori[factor_name] = df_ori['factor'] \
                          / df_ori['factor'].unstack().rolling(5,1).apply(lambda x : f_calc_cv(x)).stack()
    df_ori = df_ori[df_ori['para'] > 1e-5]
    # df_ori[factor_name] = df_ori[factor_name] - df_ori[factor_name].unstack().median(axis=1)
    # df_ori[factor_name] = df_ori[factor_name].unstack().rolling(50,1).mean().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]