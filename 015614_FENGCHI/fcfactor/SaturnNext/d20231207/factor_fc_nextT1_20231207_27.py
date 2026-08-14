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

def factor_fc_nextT1_20231207_27(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['VALUE_DIFF_INSTITUTE'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['VALUE_DIFF_INSTITUTE'].unstack().rolling(3, min_periods=1).mean().stack()
    a = md_data['VALUE_DIFF_INSTITUTE'].unstack().rolling(10, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    特大单买额-特大单卖额，近3日与近2周均值之差
    20.33 0.025  
    =====>>>> 20.333333333333336 0.02595150328908955 825.7702955285971 3135.4731911374115 xly_t_1_md_tz147，wj_last_af_bid 0.3604，0.3169
    """
    return factor_df