# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240328_8(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['NET_INFLOW_RATE_VOLUME'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['NET_INFLOW_RATE_VOLUME'].unstack().rolling(2, min_periods=1).mean().stack()
    a = md_data['NET_INFLOW_RATE_VOLUME'].unstack().rolling(90, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    当日主力净流入量/成交股数，近2日相对于近90天的差值
    =====>>>> 26.667 0.056 0.00916720389729181 0.175404523155289 fc_LastZtLastTrans_20240314_5，Institute_earn 0.6801，0.5237
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df