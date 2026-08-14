# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20230928_1(start_date, end_date, IO, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['NET_INFLOW_RATE_VALUE_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['NET_INFLOW_RATE_VALUE_L'].unstack().rolling(2, min_periods=1).mean().stack() * 100
    a = md_data['NET_INFLOW_RATE_VALUE_L'].unstack().rolling(240, min_periods=1).mean().stack() * 100

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    最近2天大单净流入比例，相对于近一年以来大单净流入比例的差值
    39.25 -0.06922
    =====>>>> 39.25 -0.06922378796620275 170.15449147661283 1400.6222910113202 skk_pct_turn_max，xbc_20230921_3 0.5018，0.5001
    """
    return factor_df


