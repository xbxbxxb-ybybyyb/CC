import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# pct/pre的T-1除以20日变异系数
# 27,-0.072,-0.074
factor_name = 'qyh_sat_md_20240111_7'
def factor_qyh_sat_md_20240111_7(start_date, end_date, IO, return_fillna_dic=False):
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
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt','pct_chg'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['factor'] = df_ori.eval('pct_chg / pre_close')
    df_ori[factor_name] = df_ori['factor'] / df_ori['factor'].unstack().rolling(20,1).apply(lambda x : f_calc_cv(x)).stack()
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]