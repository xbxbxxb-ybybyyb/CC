import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_pos60'
def factor_qyh_pos60(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['max'] = df_ori['close'].unstack().rolling(60,5).max().stack()
    df_ori['min'] = df_ori['close'].unstack().rolling(60,5).min().stack()
    df_ori[factor_name] = (df_ori['close'] - df_ori['min']) / (df_ori['max'] - df_ori['min'])
    df_ori[factor_name] = (df_ori[factor_name] - 0.5) * 2 # [-1,1]
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
