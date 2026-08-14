# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240411_6(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['OPEN_NET_INFLOW_RATE_VALUE_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['OPEN_NET_INFLOW_RATE_VALUE_L'].unstack().rolling(3, min_periods=1).mean().stack()
    a = md_data['OPEN_NET_INFLOW_RATE_VALUE_L'].unstack().rolling(60, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    10点前的主力净流入金额/10点前的成交金额，近3日均值相对于近3个月的差值
    =====>>>> 19.0 -0.045 1.8952958554343438 5.354446372712815 qyh_sat_lztick_20240314_2，fc_T1_20240328_12 0.4054，0.3984
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df