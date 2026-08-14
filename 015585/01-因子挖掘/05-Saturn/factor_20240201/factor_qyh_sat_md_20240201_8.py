import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# amt的5日和20日偏度比例
# 0.043，15，0.049
factor_name = 'qyh_sat_md_20240201_8'
def factor_qyh_sat_md_20240201_8(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    def f_calc_skew(factor_series):
        factor_series = factor_series[~np.isnan(factor_series)]
        mean = factor_series.mean()
        std = factor_series.std(ddof=1)
        n = len(factor_series)
        if n > 3:
            skew = sum(((factor_series - mean) / std) ** 3) * n / (n - 1) / (n - 2)
        else:
            skew = np.nan
        return skew
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt','pct_chg'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    # df_ori['factor'] = np.log(abs(df_ori['pct_chg']) + 0.001) * df_ori['amt']
    # df_ori = df_ori[df_ori['amt'] > 0]
    # df_ori.loc[df_ori['zcz']==1,'factor'] = (df_ori.loc[df_ori['zcz']==1,'factor']-1) / 2 + 1
    df_ori[factor_name] = df_ori['amt'].unstack().rolling(5,1).apply(lambda x : f_calc_skew(x)).stack() \
                          / (df_ori['amt'].unstack().rolling(20,1).apply(lambda x : f_calc_skew(x)).stack())
    #
    # df_ori[factor_name] = df_ori[factor_name] - df_ori[factor_name].unstack().median(axis=1)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]