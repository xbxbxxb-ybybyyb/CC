# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240509_3(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['SELL_VALUE_MED_ORDER_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['SELL_VALUE_MED_ORDER_ACT'].unstack().rolling(6, min_periods=1).mean().stack()
    a = md_data['SELL_VALUE_MED_ORDER_ACT'].unstack().rolling(30, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    近1周中户卖出金额相对于近1个月均值之差
    =====>>>> 16.875 -0.015 1000.0013001049036 2589.0962934395275 amt_compared_5，qyh_sat_md_20240111_6 0.6903，0.6188
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df