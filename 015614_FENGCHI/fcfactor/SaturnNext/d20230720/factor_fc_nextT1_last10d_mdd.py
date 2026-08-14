# coding: utf-8
# Author：fengchi863
# Date ：2023/7/4 20:52

import pandas as pd
from xquant.factordata import FactorData
import numpy as np
s = FactorData()

def calc_mdd(_s):
    mdd = (np.maximum.accumulate(np.nancumsum(_s)) - np.nancumsum(_s)).max()
    return -mdd

def factor_fc_nextT1_last10d_mdd(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -11)[0])
    md_data = IO.read_data([start_date_, end_date], alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

    md_data.loc[md_data['pct_chg'] > 10, 'pct_chg'] = 10
    md_data.loc[md_data['pct_chg'] < -10, 'pct_chg'] = -10

    factor_df = pd.DataFrame()
    factor_df[factor_name] = md_data['pct_chg'].unstack().rolling(10, min_periods=3).apply(lambda x: calc_mdd(x)).stack()
    # -------------------------------------------------------过去10天的最大回撤---26.38 -5.31-----------------------------------------------------------
    return factor_df