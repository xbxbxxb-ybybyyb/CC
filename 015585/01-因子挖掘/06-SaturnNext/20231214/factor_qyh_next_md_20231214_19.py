import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# 上影线-下影线在6日剔除停牌后，与amt乘积的最小值/amt最小值
# 18，0.038
#
factor_name = 'qyh_next_md_20231214_19'
def factor_qyh_next_md_20231214_19(start_date, end_date, IO, return_fillna_dic=False):
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
                          columns=['low','close','pre_close','high','adjfactor','pct_chg','amt'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['syx1'] = (df_ori['high'] - df_ori['close']) / df_ori['pre_close']
    df_ori['xyx1'] = (df_ori['close'] - df_ori['low']) / df_ori['pre_close']
    df_ori['factor'] = df_ori['syx1'] - df_ori['xyx1']
    df_ori = df_ori[df_ori['amt']>0]
    df_ori['factor1'] = (df_ori['factor'] * df_ori['amt']).unstack().rolling(6,1).min().stack()
    df_ori['factor2'] = df_ori['amt'].unstack().rolling(6,1).min().stack()
    df_ori[factor_name] = (df_ori['factor1']) / (df_ori['factor2'])
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]