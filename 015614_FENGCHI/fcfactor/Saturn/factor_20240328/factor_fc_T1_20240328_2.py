# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240328_2(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['BUY_VOLUME_SMALL_ORDER_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['BUY_VOLUME_SMALL_ORDER_ACT'].unstack().rolling(1, min_periods=1).mean().stack()
    a = md_data['BUY_VOLUME_SMALL_ORDER_ACT'].unstack().rolling(2, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    昨日散户买入总量(仅主动)，相对于近2日均值的差值
    =====>>>> 23.792 0.061 29.87163013436733 182.16314105443954 xly_newsat_md3_3_0，fc_T1_20240321_11，fc_T1_20240321_1 1.0，0.6764，0.6002
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df