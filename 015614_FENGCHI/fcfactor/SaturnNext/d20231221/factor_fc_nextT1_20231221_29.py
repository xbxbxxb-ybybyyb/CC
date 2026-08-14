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

def factor_fc_nextT1_20231221_29(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['SELL_TRADES_LARGE_ORDER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['SELL_TRADES_LARGE_ORDER'].unstack().rolling(3, min_periods=1).median().stack()
    a = md_data['SELL_TRADES_LARGE_ORDER'].unstack().rolling(10, min_periods=1).median().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    当日卖出大单的单数，最近3日中位值与最近两周中位数之差
    18.375 -0.044
    =====>>>> 18.375 -0.04418489088072184 134.69814003966917 213.40052318835734 fc_nextT1_20231130_11，xly_t_1_md_tz55 0.6433，0.6281
    """
    return factor_df