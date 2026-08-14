import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_vol_5_2max'

def factor_qyh_md_vol_5_2max(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.35,'data':['md']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -100)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['volume','adjfactor'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['volume'] = df_ori['volume'] / df_ori['adjfactor']
    df_ori['v5_mean'] = df_ori['volume'].unstack().rolling(5 , 1).mean().stack()
    df_ori['v60_max'] = df_ori['volume'].unstack().rolling(60, 10).max().stack()
    df_ori['res1'] = df_ori['v5_mean'] / (df_ori['v60_max']+1)
    df_ori[factor_name] = df_ori['res1']

    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
