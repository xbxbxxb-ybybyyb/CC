import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# abs(pct*turn)的T-1/120日均值
# 28，-0.079
# zwh_20230705_001：27
factor_name = 'qyh_next_md_20231214_7'
def factor_qyh_next_md_20231214_7(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -180)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['turn','pct_chg','close','vwap','pre_close','open','low'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['factor'] = abs(df_ori['pct_chg'] * df_ori['turn'])
    df_ori['factor1'] = df_ori['factor']
    df_ori['factor2'] = df_ori['factor'].unstack().rolling(120,1).mean().stack()
    df_ori[factor_name] = df_ori['factor1'] / (df_ori['factor2'] + 1e-8)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]