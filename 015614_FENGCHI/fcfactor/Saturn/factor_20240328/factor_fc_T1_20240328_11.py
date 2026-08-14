# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240328_11(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['NET_INFLOW_RATE_VOLUME_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['NET_INFLOW_RATE_VOLUME_L'].unstack().rolling(6, min_periods=1).mean().stack()
    a = md_data['NET_INFLOW_RATE_VOLUME_L'].unstack().rolling(10, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    当日主力净流入量/成交股数，近一周相对于近2周均值的差异
    =====>>>> 14.458 -0.048 1.6646753629488593 3.510292851549515 qyh_sat_md_20240201_7，sss_big2ratio_5 0.421，0.3576
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df