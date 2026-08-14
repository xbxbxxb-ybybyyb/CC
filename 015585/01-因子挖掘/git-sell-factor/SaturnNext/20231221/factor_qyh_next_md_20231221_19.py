import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_next_md_20231221_19'
def factor_qyh_next_md_20231221_19(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    def f_calc_m2m(factor_series):
        factor_series = factor_series[~np.isnan(factor_series)]
        return factor_series.max() / factor_series.mean() if factor_series.mean() > 0 else np.nan
    start_date = int(s.tradingday(str(start_date), -180)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['amt','vwap','pct_chg','high','low','close','pre_close','turn'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['factor'] = df_ori['low'] / df_ori['vwap']
    df_ori[factor_name] = (df_ori['factor']).unstack().rolling(5,1).apply(lambda x : f_calc_m2m(x)).stack() \
                          / df_ori['factor'].unstack().rolling(60,1).apply(lambda x : f_calc_m2m(x)).stack()
    #
    df_ori['tmp'] = (df_ori['close'] - df_ori['pre_close'])/(df_ori['high'] + df_ori['low'])*2
    df_ori['tmp'] = df_ori['tmp'].unstack().rolling(5,1).mean().stack()
    df_ori.loc[df_ori['tmp'] < -0.0047,factor_name] = df_ori.loc[df_ori['tmp'] < -0.0047,factor_name] - 0.02

    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]