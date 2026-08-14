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

def factor_fc_nextT1_20231221_46(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['VALUE_DIFF_INSTITUTE_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['VALUE_DIFF_INSTITUTE_ACT'].unstack().rolling(2, min_periods=1).median().stack()
    a = md_data['VALUE_DIFF_INSTITUTE_ACT'].unstack().rolling(30, min_periods=1).median().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    特大单主动买额-特大单主动卖额，昨日与近一个月中位数的delta
    15.166 0.0394 
    =====>>>> 15.166666666666668 0.03942678774529855 -30.180447595523695 4993.428723503211 fc_nextT1_20230921_11，fc_nextT1_20231214_1 0.4701，0.443
    """
    return factor_df