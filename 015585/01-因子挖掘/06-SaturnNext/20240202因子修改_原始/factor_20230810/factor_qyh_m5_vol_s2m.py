
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_vol_s2m'
def factor_qyh_m5_vol_s2m(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.01,'data':['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    amt_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/amt.h5')
    amt_data_pct = pd.DataFrame()
    for col in amt_data.columns:
        amt_data_pct[col] = amt_data[col] / amt_data.sum(axis=1)
    #
    amt_mall = amt_data.sum(axis=1).groupby('dt').sum()
    amt_data_m_pct = pd.DataFrame(index = amt_mall.index)
    for col in amt_data.columns:
        amt_data_m_pct[col] = amt_data[col].groupby('dt').sum() / amt_mall
    #
    res = amt_data_pct - amt_data_m_pct
    res = pd.DataFrame(abs(res).mean(axis = 1),columns=[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return res