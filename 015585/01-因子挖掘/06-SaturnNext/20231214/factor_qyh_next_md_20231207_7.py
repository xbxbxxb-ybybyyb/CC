import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# t-1日turn / 20日最小值
# 31,-0.056
#
factor_name = 'qyh_next_md_20231207_7'
def factor_qyh_next_md_20231207_7(start_date, end_date, IO, return_fillna_dic=False):
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
                          columns=['amt','pct_chg','turn'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    # df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
    #             df_ori.reset_index()['dt'] >= '2020-08-24'))
    #              | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    # df_ori.loc[df_ori['zcz'] == 1, 'close'] = (df_ori.loc[df_ori['zcz'] == 1, 'close'] / df_ori.loc[df_ori['zcz'] == 1, 'pre_close'] -1)/2+1
    # df_ori.loc[df_ori['zcz'] == 1, 'vwap'] = (df_ori.loc[df_ori['zcz'] == 1, 'vwap'] / df_ori.loc[df_ori['zcz'] == 1, 'pre_close'] -1)/2+1
    #
    df_ori[factor_name] = (df_ori['turn'] /(df_ori['turn'].unstack().rolling(20,1).min().stack()+1e-8))
    # df_ori[factor_name] = rank_(df_ori[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]