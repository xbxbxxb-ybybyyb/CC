# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240328_1(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['CLOSE_MONEYFLOW_PCT_VALUE_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['CLOSE_MONEYFLOW_PCT_VALUE_L'].unstack().rolling(1, min_periods=1).mean().stack()
    a = md_data['CLOSE_MONEYFLOW_PCT_VALUE_L'].unstack().rolling(60, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    昨天14:30后的主力净流入金额/流通市值，相对于近3个月的差值
    =====>>>> 19.75 0.051 0.19738674935940762 0.431597881785923 wj_lastend_bamtstd1，qyh_sat_lztick_20240321_5 0.4827，0.4436
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df