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

def factor_fc_nextT1_20231221_14(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['BUY_TRADES_SMALL_ORDER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['BUY_TRADES_SMALL_ORDER'].unstack().rolling(3, min_periods=1).median().stack()
    a = md_data['BUY_TRADES_SMALL_ORDER'].unstack().rolling(20, min_periods=1).median().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    当日买入小单的单数，长短期中位值之差
    29.5 -0.067
    =====>>>> 29.500000000000004 -0.06708399442594473 3488.941300849519 7457.10651886687 fc_nextT1_20231130_2，wj_last20_diff 0.6617，0.6485
    """
    return factor_df