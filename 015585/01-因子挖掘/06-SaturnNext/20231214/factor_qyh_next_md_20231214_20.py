import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# abs(pct * turn)的5日均值/10日均值
# 26，-0.053
#
factor_name = 'qyh_next_md_20231214_20'
def factor_qyh_next_md_20231214_20(start_date, end_date, IO, return_fillna_dic=False):
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
    def rank_(data_):
        data_r = (data_.unstack().rank(axis=1) / (~ data_.unstack().isnull()).values.sum(axis=1).reshape(-1, 1)).stack()
        return data_r
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['adjfactor','pct_chg','turn'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['factor'] = abs(df_ori['pct_chg'] * df_ori['turn'])
    # df_ori = df_ori[df_ori['amt']>0]
    df_ori['factor1'] = (df_ori['factor']).unstack().rolling(5,1).mean().stack()
    df_ori['factor2'] = df_ori['factor'].unstack().rolling(10,1).mean().stack()
    df_ori[factor_name] = (df_ori['factor1']+1e-8) / (df_ori['factor2']+1e-8)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]