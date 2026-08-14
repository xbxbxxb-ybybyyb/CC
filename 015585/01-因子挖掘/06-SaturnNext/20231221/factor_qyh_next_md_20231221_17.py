import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# abs（pct*turn)的5日集中度和10日的差异
# 20,0.058,0.062
#
factor_name = 'qyh_next_md_20231221_17'
def factor_qyh_next_md_20231221_17(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0.12,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    def f_calc_sum(factor_series):
        return factor_series[~np.isnan(factor_series)].sum()
    def f_calc_cct(factor_series):
        if abs(f_calc_sum(factor_series)) > 0:
            return f_calc_sum(factor_series ** 2) / (f_calc_sum(factor_series) ** 2)
        else:
            return np.nan
    start_date = int(s.tradingday(str(start_date), -180)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['amt','vwap','pct_chg','high','low','close','pre_close','turn'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['factor'] = abs(df_ori['pct_chg'] * df_ori['turn'])
    df_ori['factor'] = df_ori['factor'].unstack().fillna(method = 'ffill',limit = 20).stack()
    df_ori[factor_name] = df_ori['factor'].unstack().rolling(5,1).apply(lambda x : f_calc_cct(x)).stack() \
                          - df_ori['factor'].unstack().rolling(10,1).apply(lambda x : f_calc_cct(x)).stack()
    #
    # df_ori['tmp'] = (df_ori['close'] - df_ori['pre_close'])/(df_ori['high'] + df_ori['low'])*2
    # df_ori['tmp'] = df_ori['tmp'].unstack().rolling(5,1).mean().stack()
    # df_ori.loc[df_ori['tmp'] < -0.0047,factor_name] = df_ori.loc[df_ori['tmp'] < -0.0047,factor_name] - 2*0.26

    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]