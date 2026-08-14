import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_amp_250_update'

def factor_qyh_amp_250_update(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.3,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -300)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close','adjfactor'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['close'] = df_ori['close'] * df_ori['adjfactor']
    df_ori['max'] = df_ori['close'].unstack().rolling(250,50).max().stack()
    df_ori['min'] = df_ori['close'].unstack().rolling(250,50).min().stack()
    df_ori[factor_name] = df_ori['max'] / df_ori['min'] - 1
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
