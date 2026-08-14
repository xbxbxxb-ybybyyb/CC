import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_next_md_20231207_12'
def factor_qyh_next_md_20231207_12(start_date, end_date, IO, return_fillna_dic=False):
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
    start_date = int(s.tradingday(str(start_date), -150)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['high','low','pre_close','close','amt','vwap'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['factor'] = df_ori['high'] / df_ori['vwap']
    df_ori['factor1'] = df_ori['factor'].unstack().rolling(10,1).apply(lambda x : f_calc_cct(x)).stack()
    df_ori['factor2'] = df_ori['factor'].unstack().rolling(60,1).apply(lambda x : f_calc_cct(x)).stack()
    df_ori[factor_name] = df_ori['factor1'] / df_ori['factor2']
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]