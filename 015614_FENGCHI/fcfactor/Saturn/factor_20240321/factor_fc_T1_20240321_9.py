# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240321_9(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['BUY_TRADES_LARGE_ORDER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['BUY_TRADES_LARGE_ORDER'].unstack().rolling(120, min_periods=1).mean().stack()
    a = md_data['BUY_TRADES_LARGE_ORDER'].unstack().rolling(240, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    当日买入大单的单数，近半年相对于近1年的比值
    =====>>>> 13.625 0.011 -1.5293750324794602 76.26317104267557 zwh_20240229_021，xbc_20240103_12 0.3287，0.2845
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df