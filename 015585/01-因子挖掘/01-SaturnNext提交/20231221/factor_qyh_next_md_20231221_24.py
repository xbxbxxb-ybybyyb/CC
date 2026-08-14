import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_next_md_20231221_24'
def factor_qyh_next_md_20231221_24(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -180)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['pre_close','adjfactor','open'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    for col in ['open','pre_close']:
        df_ori[col] = df_ori[col] * df_ori['adjfactor']
    df_ori[factor_name] = (df_ori['open']).unstack().rolling(5,1).min().stack() \
                          / df_ori['pre_close']
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]