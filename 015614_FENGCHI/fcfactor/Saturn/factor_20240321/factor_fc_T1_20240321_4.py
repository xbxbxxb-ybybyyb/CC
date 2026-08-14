# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240321_4(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['BUY_TRADES_LARGE_ORDER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['BUY_TRADES_LARGE_ORDER'].unstack().rolling(1, min_periods=1).mean().stack()
    a = md_data['BUY_TRADES_LARGE_ORDER'].unstack().rolling(90, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    当日买入大单的单数，前一日相对于最近3个月的比例
    =====>>>> 27.833 0.043 158.77812188627166 278.18918775042926 wd_lzo_near_ul_bid_amt，qyh_sat_lztick_20240314_1 0.6931，0.5831
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df