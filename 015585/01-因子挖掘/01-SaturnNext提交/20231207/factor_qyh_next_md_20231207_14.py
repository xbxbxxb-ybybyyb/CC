import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_next_md_20231207_14'
def factor_qyh_next_md_20231207_14(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -150)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['high','low','pct_chg','close','amt','vwap'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['factor'] = df_ori['pct_chg'] * df_ori['amt']
    df_ori['factor1'] = df_ori['factor'].unstack().rolling(10,1).median().stack()
    df_ori['factor2'] = df_ori['amt'].unstack().rolling(10,1).median().stack()
    df_ori[factor_name] = df_ori['factor1'] / (df_ori['factor2']+1)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]