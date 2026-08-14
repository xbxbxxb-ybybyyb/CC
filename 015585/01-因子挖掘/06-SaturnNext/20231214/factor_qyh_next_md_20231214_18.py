import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# amt的5日位置/60日位置
# 26，0.058
#
factor_name = 'qyh_next_md_20231214_18'
def factor_qyh_next_md_20231214_18(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    def f_calc_pos(factor_series):
        factor_series = factor_series[~np.isnan(factor_series)]
        return (factor_series[-1] - factor_series.min()) / \
               (factor_series.max() - factor_series.min() + 1e-8)
    def rank_(data_):
        data_r = (data_.unstack().rank(axis=1) / (~ data_.unstack().isnull()).values.sum(axis=1).reshape(-1, 1)).stack()
        return data_r
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['turn','close','pre_close','vwap','adjfactor','pct_chg','amt'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['factor'] = df_ori['amt']
    df_ori['factor1'] = df_ori['factor'].unstack().rolling(5,1).apply(lambda x : f_calc_pos(x)).stack()
    df_ori['factor2'] = df_ori['factor'].unstack().rolling(60,1).apply(lambda x : f_calc_pos(x)).stack()
    df_ori[factor_name] = (df_ori['factor1']+1) / (df_ori['factor2']+1e-2)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]