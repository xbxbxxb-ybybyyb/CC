# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240321_5(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['BUY_TRADES_SMALL_ORDER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['BUY_TRADES_SMALL_ORDER'].unstack().rolling(1, min_periods=1).mean().stack()
    a = md_data['BUY_TRADES_SMALL_ORDER'].unstack().rolling(2, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    当日买入小单的单数，最近两日的差值
    =====>>>> 19.833 0.048 369.81277765639794 3424.844586790899 Lzt_latest_last_order_time_cost，wj_last_lflow_rate 0.4331，0.4263
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df