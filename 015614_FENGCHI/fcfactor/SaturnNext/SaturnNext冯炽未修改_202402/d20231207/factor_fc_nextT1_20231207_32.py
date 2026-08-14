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

def factor_fc_nextT1_20231207_32(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['VALUE_DIFF_LARGE_TRADER_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['VALUE_DIFF_LARGE_TRADER_ACT'].unstack().rolling(2, min_periods=1).mean().stack()
    a = md_data['VALUE_DIFF_LARGE_TRADER_ACT'].unstack().rolling(30, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    大单主动买额-大单主动卖额，长短期平均值对应差值
    35.7916 0.063  
    =====>>>> 35.79166666666667 0.06362681355062463 -520.1210774534002 1976.4239611549885 xly_t_1_md_tz150，fc_nextT1_large_trade_act 0.5891，0.5568
    """
    return factor_df