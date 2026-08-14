# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240418_2(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['SELL_TRADES_SMALL_ORDER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['SELL_TRADES_SMALL_ORDER'].unstack().rolling(1, min_periods=1).mean().stack()
    a = md_data['SELL_TRADES_SMALL_ORDER'].unstack().rolling(40, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    昨日小单净流入量相对于近两个月以来的均值
    =====>>>> 34.542 0.048 5213.390081359469 7937.394079362311 qyh_sat_lztick_20240314_1，xly_newsat_md10 0.6947，0.6696
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df