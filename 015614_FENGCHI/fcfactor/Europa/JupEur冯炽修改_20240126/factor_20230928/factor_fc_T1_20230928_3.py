# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20230928_3(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['NET_INFLOW_RATE_VALUE_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['NET_INFLOW_RATE_VALUE_L'].unstack().rolling(3, min_periods=1).mean().stack() * 100
    a = md_data['NET_INFLOW_RATE_VALUE_L'].unstack().rolling(120, min_periods=1).mean().stack() * 100

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    最近3天大单净流入比例，相对于近半年以来大单净流入比例的差值
    30.33 -0.06195
    =====>>>> 30.333333333333336 -0.06194629024044162 141.54334482662665 1220.4554928497005 slxd，skk_pct_mdiff_mean 0.4776，0.457
!!!! fc_T1_20230928_1 0.8333208359846531
!!!! fc_T1_20230928_2 0.732094380031969
    """
    return factor_df


