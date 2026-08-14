# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240418_5(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['SELL_TRADES_LARGE_ORDER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['SELL_TRADES_LARGE_ORDER'].unstack().rolling(40, min_periods=1).mean().stack()
    a = md_data['SELL_TRADES_LARGE_ORDER'].unstack().rolling(240, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    近2个月卖出大单的单数相对于近一年的差值
    =====>>>> 18.083 0.014 10.39265969309105 146.44297883431648 fc_T1_20240321_9，xbc_20240103_12 0.6654，0.5237
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df