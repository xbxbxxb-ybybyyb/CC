# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240321_8(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['BUY_TRADES_EXLARGE_ORDER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['BUY_TRADES_EXLARGE_ORDER'].unstack().rolling(6, min_periods=1).mean().stack()
    a = md_data['BUY_TRADES_EXLARGE_ORDER'].unstack().rolling(30, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    当日买入超大单的单数，近1周相对于近1个月的比例
    =====>>>> 15.417 -0.013 9.416773193846145 26.329735562473456 amt_compared_5，skk_20240307_4 0.666，0.5899
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df