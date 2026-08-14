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

def factor_fc_nextT1_20231207_34(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['VALUE_DIFF_SMALL_TRADER_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['VALUE_DIFF_SMALL_TRADER_ACT'].unstack().rolling(2, min_periods=1).mean().stack()
    a = md_data['VALUE_DIFF_SMALL_TRADER_ACT'].unstack().rolling(10, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    小单主动买额-小单主动卖额，近2日与近2周均值之差
    18.875 -0.0443
    =====>>>> 18.875 -0.044356982667994975 206.0182118327987 1256.5659835067102 sss_smallflow_s2_5_s，fc_nextT1_20230817_4 0.4682，0.4015
    """
    return factor_df