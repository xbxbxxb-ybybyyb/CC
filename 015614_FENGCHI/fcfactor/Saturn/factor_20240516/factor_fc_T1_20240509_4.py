# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240509_4(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['SELL_VALUE_MED_ORDER_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['SELL_VALUE_MED_ORDER_ACT'].unstack().rolling(1, min_periods=1).mean().stack()
    a = md_data['SELL_VALUE_MED_ORDER_ACT'].unstack().rolling(5, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    昨日中户卖出金额相对于近一周均值之差
    =====>>>> 13.292 0.032 2098.422499388971 3109.037146852398 fc_T1_20240321_11，fc_T1_20240321_1 0.6606，0.6016
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df