# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240418_1(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['SELL_TRADES_MED_ORDER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['SELL_TRADES_MED_ORDER'].unstack().rolling(1, min_periods=1).mean().stack()
    a = md_data['SELL_TRADES_MED_ORDER'].unstack().rolling(2, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    ZT日卖出中单的单数，相对于前日的均值的比值
    =====>>>> 47.833 0.095 310.1317638919234 547.1205444266644 fc_T1_20240321_1，fc_T1_20240321_2，fc_T1_20240321_11 0.846，0.6793，0.6541
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df