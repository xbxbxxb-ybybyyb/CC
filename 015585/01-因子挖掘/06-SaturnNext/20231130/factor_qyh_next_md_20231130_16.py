import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# 上影线的5日变异系数
# 33,-0.066
factor_name = 'qyh_next_md_20231130_16'
def factor_qyh_next_md_20231130_16(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    def rank_(data_):
        data_r = (data_.unstack().rank(axis=1) / (~ data_.unstack().isnull()).values.sum(axis=1).reshape(-1, 1)).stack()
        return data_r

    def f_calc_avg(factor_series):
        return factor_series[~np.isnan(factor_series)].mean()
    def f_calc_cv(factor_series):
        if abs(f_calc_avg(factor_series)) > 0:
            return np.std(factor_series[~np.isnan(factor_series)], ddof=1) / f_calc_avg(factor_series)
        else:
            return np.nan
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close','pre_close','high','low'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    # df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
    #             df_ori.reset_index()['dt'] >= '2020-08-24'))
    #              | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    #
    # df_ori['factor'] = (df_ori['pct_chg'] - df_ori['low']) / df_ori['pre_close']
    #
    df_ori['factor'] = (df_ori['high'] - df_ori['close']) / df_ori['pre_close']
    df_ori[factor_name] = df_ori['factor'].unstack().rolling(5,2).apply(lambda x : f_calc_cv(x)).stack()
    # df_ori[factor_name] = df_ori[factor_name].apply(lambda x : np.log(x+1))
    # df_ori[factor_name] = rank_(df_ori[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
