# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20230921_10(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['CLOSE_NET_INFLOW_RATE_VALU_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['CLOSE_NET_INFLOW_RATE_VALU_L'].unstack().rolling(3, min_periods=1).mean().stack() * 100
    a = md_data['CLOSE_NET_INFLOW_RATE_VALU_L'].unstack().rolling(240, min_periods=1).mean().stack() * 100

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    两点半以后的大单流入金额，短期与长期的差值
    21.833333333333336 -0.05492624383821723 10.429660445015424 199.29405630240336 wj_last2_moneyflow_endbig，xbc_20230823_2 0.6525，0.4042
    21.83 -0.05493
    """
    return factor_df


