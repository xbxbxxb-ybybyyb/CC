# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20230928_2(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['NET_INFLOW_RATE_VALUE_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['NET_INFLOW_RATE_VALUE_L'].unstack().rolling(6, min_periods=1).mean().stack() * 100
    a = md_data['NET_INFLOW_RATE_VALUE_L'].unstack().rolling(240, min_periods=1).mean().stack() * 100

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    最近1周大单净流入比例，相对于近一年以来大单净流入比例的差值
    37.58 -0.06651
    =====>>>> 37.583333333333336 -0.06650939829969187 53.32689316781697 1038.183433277764 skk_pct_turn_r7，EFS_pct5_T1 0.4632，0.4599
    """
    return factor_df


