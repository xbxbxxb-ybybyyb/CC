import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_next_md_20231214_9'
def factor_qyh_next_md_20231214_9(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    def pos(factor_series):
        factor_series = factor_series[~np.isnan(factor_series)]
        return (factor_series[-1] - factor_series.min()) / (factor_series.max() - factor_series.min() + 1e-8)
    start_date = int(s.tradingday(str(start_date), -180)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['turn','pct_chg'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['factor'] = abs(df_ori['turn'])
    df_ori['factor1'] = df_ori['factor'].unstack().rolling(10,1).apply(lambda x :pos(x)).stack()
    df_ori['factor2'] = df_ori['factor'].unstack().rolling(80,1).apply(lambda x :pos(x)).stack()
    df_ori[factor_name] = df_ori['factor1'] - (df_ori['factor2'] + 1e-8)

    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]