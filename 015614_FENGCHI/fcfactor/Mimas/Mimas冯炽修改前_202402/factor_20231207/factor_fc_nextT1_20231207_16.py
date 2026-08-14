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

def factor_fc_nextT1_20231207_16(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['SELL_VALUE_SMALL_ORDER_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['SELL_VALUE_SMALL_ORDER_ACT'].unstack().rolling(1, min_periods=1).mean().stack()
    a = md_data['SELL_VALUE_SMALL_ORDER_ACT'].unstack().rolling(10, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    散户主动卖出金额昨日与近2周均值之差
    14.41 -0.039  
    =====>>>> 14.416666666666668 -0.039559773068125526 2342.447276716461 2626.459914382202 xly_t_1_md_tz55，fc_nextT1_20230803_2 0.6852，0.655
    """
    return factor_df