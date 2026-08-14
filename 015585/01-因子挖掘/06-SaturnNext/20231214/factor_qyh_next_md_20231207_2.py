import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# abs(pct*turn)在5日和240日离散程度的差异比值
# 28,0.067
#
factor_name = 'qyh_next_md_20231207_2'
def factor_qyh_next_md_20231207_2(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    def f_calc_m2m(factor_series):
        factor_series = factor_series[~np.isnan(factor_series)]
        return factor_series.max() / factor_series.mean() if factor_series.mean() > 0 else np.nan
    def rank_(data_):
        data_r = (data_.unstack().rank(axis=1) / (~ data_.unstack().isnull()).values.sum(axis=1).reshape(-1, 1)).stack()
        return data_r
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['turn','pct_chg'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    # df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
    #             df_ori.reset_index()['dt'] >= '2020-08-24'))
    #              | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    #
    df_ori['factor'] = abs(df_ori['pct_chg']) * df_ori['turn']
    df_ori['factor1'] = df_ori['factor'].unstack().rolling(5,1).apply(lambda x : f_calc_m2m(x)).stack()
    df_ori['factor2'] = df_ori['factor'].unstack().rolling(240,1).apply(lambda x : f_calc_m2m(x)).stack()
    df_ori[factor_name] = df_ori['factor1'] / (df_ori['factor2']+1e-8)
    # df_ori[factor_name] = rank_(df_ori[factor_name])
    # df_ori.loc[df_ori['zcz']==1,factor_name] = df_ori.loc[df_ori['zcz']==1,factor_name]/2
    # df_ori[factor_name] = df_ori[factor_name].unstack().rolling(2,1).mean().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]