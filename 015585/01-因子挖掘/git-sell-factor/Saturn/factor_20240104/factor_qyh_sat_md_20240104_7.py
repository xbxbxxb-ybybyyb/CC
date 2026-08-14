import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_sat_md_20240104_7'
def factor_qyh_sat_md_20240104_7(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','close','high','low','amt','pct_chg','turn'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori = df_ori[df_ori['turn'] > 0]
    df_ori['factor'] = df_ori['pct_chg'] * df_ori['turn']
    df_ori['factor1'] = df_ori['pct_chg'].unstack().rolling(5,1).min().stack() * df_ori['turn'].unstack().rolling(5,1).max().stack()
    df_ori['factor2'] = df_ori['pct_chg'].unstack().rolling(5,1).min().stack() * df_ori['turn'].unstack().rolling(5,1).min().stack()
    df_ori[factor_name] = df_ori[['factor1','factor2']].min(axis=1)
    #
    df_ori[factor_name] = df_ori[factor_name] - df_ori[factor_name].unstack().mean(axis=1)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]