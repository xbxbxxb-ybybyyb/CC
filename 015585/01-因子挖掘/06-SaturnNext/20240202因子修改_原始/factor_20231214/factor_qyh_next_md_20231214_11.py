import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_next_md_20231214_11'
def factor_qyh_next_md_20231214_11(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:4.25,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -180)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','pct_chg','turn'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['factor'] = abs(df_ori['pct_chg'] * df_ori['turn'])
    df_ori = df_ori[df_ori['factor'] > 0]
    df_ori['factor1'] = df_ori['factor'].unstack().shift(1).stack() + 2 * df_ori['factor']
    df_ori['factor2'] = df_ori['factor'].unstack().rolling(20,1).median().stack()
    df_ori[factor_name] = df_ori['factor1'] / (df_ori['factor2'] + 1e-5)

    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]