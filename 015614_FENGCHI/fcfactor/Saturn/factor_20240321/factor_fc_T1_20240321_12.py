# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240321_12(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['BUY_VALUE_SMALL_ORDER_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['BUY_VALUE_SMALL_ORDER_ACT'].unstack().rolling(3, min_periods=1).mean().stack()
    a = md_data['BUY_VALUE_SMALL_ORDER_ACT'].unstack().rolling(10, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    当日散户买入金额(仅主动)，最近3日相对于近2周的均值之比
    =====>>>> 16.583 -0.025 471.60117481299307 1630.7267466145258 amt_compared_5，skk_20240111_12 0.6087，0.5853
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df