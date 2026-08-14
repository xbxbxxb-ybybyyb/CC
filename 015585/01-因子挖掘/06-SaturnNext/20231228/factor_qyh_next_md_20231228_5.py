import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# 最高价的5日中位数/40中位数。全市场超额
# 26，-0.059，-0.06
# skk_20231207_40：17
factor_name = 'qyh_next_md_20231228_5'
def factor_qyh_next_md_20231228_5(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------

    start_date = int(s.tradingday(str(start_date), -180)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    for col in ['vwap','pre_close','high','low','close']:
        df_ori[col] = df_ori[col] * df_ori['adjfactor']
    df_ori[factor_name] = (df_ori['high']).unstack().rolling(5,1).median().stack() \
                          / (df_ori['high']).unstack().rolling(40,1).median().stack()
    #
    df_ori[factor_name] = df_ori[factor_name] - df_ori[factor_name].unstack().median(axis=1)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]