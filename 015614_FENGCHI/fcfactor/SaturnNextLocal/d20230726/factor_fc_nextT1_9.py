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

def factor_fc_nextT1_9(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['RISK']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -11)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['Beta'], alt='/data/group/800080/warehouse/prod/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5')

    factor_df = pd.DataFrame()
    factor_df[factor_name] = md_data['Beta'].unstack().rolling(5, min_periods=1).sum().stack()
    # -------------------------------------------------------Beta值的均值--------------------------------------------------------------
    """
    Beta
    2.083333333333333 -0.007841204825305788
    Momentum
    3.1250000000000004 0.010311846622618581
    """
    return factor_df
