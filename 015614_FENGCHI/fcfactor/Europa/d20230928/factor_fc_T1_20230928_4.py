# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20230928_4(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['NET_INFLOW_RATE_VOLUME'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['NET_INFLOW_RATE_VOLUME'].unstack().rolling(1, min_periods=1).mean().stack() * 100
    a = md_data['NET_INFLOW_RATE_VOLUME'].unstack().rolling(10, min_periods=1).mean().stack() * 100

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    昨日净流入占成交的比例，相对于近两周以来的差值
    18.625 -0.0576
    18.625 -0.05760350418287049 0.30314611456664087 21.04832690190797 xbc_20230921_2，fc_T1_20230921_14 0.6861，0.6408
    """
    return factor_df


