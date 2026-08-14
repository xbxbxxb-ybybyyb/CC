# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240328_3(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['BUY_VOLUME_SMALL_ORDER_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['BUY_VOLUME_SMALL_ORDER_ACT'].unstack().rolling(1, min_periods=1).mean().stack()
    a = md_data['BUY_VOLUME_SMALL_ORDER_ACT'].unstack().rolling(90, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    昨日散户主动买入总量，相对于近90日均值的差异
    =====>>>> 22.917 0.028 149.35325330547602 415.37029113859313 fc_T1_20240321_11，wd_lzkcs_pct_sum_d_mean 0.6584，0.6356
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df