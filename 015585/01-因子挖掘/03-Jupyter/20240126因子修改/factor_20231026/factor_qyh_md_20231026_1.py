import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_20231026_1'
def factor_qyh_md_20231026_1(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.985,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -20)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close','vwap'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori[factor_name] = (df_ori['close'] / df_ori['vwap']).unstack().rolling(5,1).min().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
