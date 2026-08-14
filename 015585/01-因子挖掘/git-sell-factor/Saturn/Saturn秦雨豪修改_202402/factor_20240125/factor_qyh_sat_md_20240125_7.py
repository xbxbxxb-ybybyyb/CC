import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_sat_md_20240125_7'
def factor_qyh_sat_md_20240125_7(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:1,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    def f_calc_sum(factor_series):
        return factor_series[~np.isnan(factor_series)].sum()

    def f_calc_cct(factor_series):
        if abs(f_calc_sum(factor_series)) > 0:
            return (f_calc_sum(factor_series ** 2)) / (f_calc_sum(factor_series) ** 2 + 1e-8)
        else:
            return np.nan
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt','pct_chg','turn'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['factor'] = (df_ori['close'] - df_ori['pre_close']) / (df_ori['vwap'])
    df_ori = df_ori[df_ori['vwap'] > 0]
    df_ori = df_ori[df_ori['amt'] > 0]
    df_ori[factor_name] = (df_ori['factor'].unstack().rolling(5,1).apply(lambda x : f_calc_cct(x)).stack()+1) \
                          / (df_ori['factor'].unstack().rolling(60,1).apply(lambda x : f_calc_cct(x)).stack()+1)
    df_ori.loc[df_ori[factor_name] >= 100, factor_name] = 100
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]