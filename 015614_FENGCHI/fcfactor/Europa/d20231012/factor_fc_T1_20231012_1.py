# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20231012_1(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['OPEN_NET_INFLOW_RATE_VOLUME_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['OPEN_NET_INFLOW_RATE_VOLUME_L'].unstack().rolling(6, min_periods=1).mean().stack() * 100
    a = md_data['OPEN_NET_INFLOW_RATE_VOLUME_L'].unstack().rolling(240, min_periods=1).mean().stack() * 100

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    最近1周开盘前半小时大单净流入比例，相对于近一年以来大单净流入比例的差值
    14.875 -0.044
    =====>>>> 14.875 -0.04405587823310736 15.43272633060805 553.2354968087647 list_len，after_not_ul_len 0.325，0.3153
    """
    return factor_df


