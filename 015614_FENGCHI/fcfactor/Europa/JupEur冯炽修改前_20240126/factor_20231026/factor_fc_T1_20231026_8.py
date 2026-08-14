# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20231026_8(start_date, end_date, IO, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['VALUE_DIFF_MED_TRADER_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['VALUE_DIFF_MED_TRADER_ACT'].unstack().rolling(1, min_periods=1).mean().stack() / 100
    a = md_data['VALUE_DIFF_MED_TRADER_ACT'].unstack().rolling(20, min_periods=1).mean().stack() / 100

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    当日中单主动买额-中单主动卖额，即净买入额，相对于近20天以来的差值
    19.958 -0.05251
    =====>>>> 19.958333333333332 -0.05250686256066875 -0.9471075986716626 20.625349717686856 fc_T1_20230928_4，xbc_20230921_2 0.6653，0.481
    """
    return factor_df


