# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240328_9(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['OPEN_MONEYFLOW_PCT_VALUE'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['OPEN_MONEYFLOW_PCT_VALUE'].unstack().rolling(1, min_periods=1).mean().stack()
    a = md_data['OPEN_MONEYFLOW_PCT_VALUE'].unstack().rolling(2, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    昨日10点前的资金净流入金额/流通市值，相对于近2日均值的差异
    =====>>>> 24.0 0.054 0.0006129633675624488 0.00831851115946638 wj_last_openamt，wj_last_StartEndMoney_diff 0.6747，0.5992
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df