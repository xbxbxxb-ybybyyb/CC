import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# 涨跌幅的6日变异系数
#
factor_name = 'qyh_sat_md_20240125_2'
def factor_qyh_sat_md_20240125_2(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:1,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -80)[0])

    def f_calc_avg(factor_series):
        return factor_series[~np.isnan(factor_series)].mean()
    def f_calc_cv(factor_series):
        if abs(f_calc_avg(factor_series)) > 0:
            return np.std(factor_series[~np.isnan(factor_series)], ddof=1) / f_calc_avg(factor_series)
        else:
            return np.nan
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt','pct_chg','open'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['factor'] = df_ori.eval('pct_chg')
    df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                df_ori.reset_index()['dt'] >= '2020-08-24'))
                 | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values

    df_ori.loc[df_ori['zcz']==1,'factor'] = (df_ori.loc[df_ori['zcz']==1,'factor']) / 2
    # df_ori = df_ori[df_ori['amt'] > 0]
    df_ori[factor_name] = df_ori['factor'] / df_ori['factor'].unstack().rolling(6,1).apply(lambda x :f_calc_cv(x)).stack()
    #
    # df_ori[factor_name] = df_ori[factor_name] - df_ori[factor_name].unstack().mean(axis=1)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]