# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240418_6(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['OPEN_NET_INFLOW_RATE_VOLUME_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['OPEN_NET_INFLOW_RATE_VOLUME_L'].unstack().rolling(2, min_periods=1).mean().stack()
    a = md_data['OPEN_NET_INFLOW_RATE_VOLUME_L'].unstack().rolling(5, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    近2日开盘主力净流入率相对于近一周的均值之差
    =====>>>> 16.167 -0.026 1.706672474328157 4.474773587752033 qyh_sat_lztick_20240314_2，wj_last_lflow_rate 0.3789，0.3721
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df