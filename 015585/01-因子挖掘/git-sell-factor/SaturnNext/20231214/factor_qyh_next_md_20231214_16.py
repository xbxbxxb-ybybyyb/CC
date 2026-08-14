import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_next_md_20231214_16'
def factor_qyh_next_md_20231214_16(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['open','close','pre_close','vwap','adjfactor','pct_chg'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['factor'] = df_ori['vwap'] * df_ori['adjfactor']
    df_ori['up'] = np.sign(df_ori['pct_chg'])
    df_ori['up'] = df_ori['up'].apply(lambda x : 1 if x >= 0.5 else np.nan)
    df_ori['factornew'] = df_ori['factor'] * df_ori['up']
    df_ori['factor1'] = df_ori['factor'].unstack().rolling(10,1).mean().stack()
    df_ori['factor2'] = df_ori['factornew'].unstack().rolling(20,1).mean().stack()
    df_ori[factor_name] = df_ori['factor1'] / (df_ori['factor2']+1e-8)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]