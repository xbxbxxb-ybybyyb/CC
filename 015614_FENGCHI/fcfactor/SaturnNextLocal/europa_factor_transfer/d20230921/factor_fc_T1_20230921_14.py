# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20230921_14(start_date, end_date, IO, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['NET_INFLOW_RATE_VALUE'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['NET_INFLOW_RATE_VALUE'].unstack().rolling(2, min_periods=1).mean().stack() * 100
    a = md_data['NET_INFLOW_RATE_VALUE'].unstack().rolling(10, min_periods=1).mean().stack() * 100

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    近2日净流入率与最近2周均值的差值
    17.875 -0.05239
    17.875 -0.05238640387464477 0.20533594559545387 14.785345829893116 hml_factor，skk_pct_turn_max 0.4467，0.435
    """
    return factor_df


