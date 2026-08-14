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

def factor_fc_nextT1_20231229_1(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['VALUE_DIFF_SMALL_TRADER_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['VALUE_DIFF_SMALL_TRADER_ACT'].unstack().rolling(2, min_periods=1).median().stack()
    a = md_data['VALUE_DIFF_SMALL_TRADER_ACT'].unstack().rolling(60, min_periods=1).median().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    小单主动买额-小单主动卖额，长短期中位数之差
    19.70 -0.048
    =====>>>> 19.708333333333336 -0.04845576907744566 328.35904596384796 1577.5216256246943 fc_nextT1_20230921_11，sss_smallflow_s2_5_s 0.5962，0.4992
    """
    return factor_df