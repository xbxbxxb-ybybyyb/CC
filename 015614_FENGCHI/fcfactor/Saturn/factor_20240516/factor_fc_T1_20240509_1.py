# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240509_1(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['SELL_VALUE_MED_ORDER_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['SELL_VALUE_MED_ORDER_ACT'].unstack().rolling(40, min_periods=1).mean().stack()
    a = md_data['SELL_VALUE_MED_ORDER_ACT'].unstack().rolling(240, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    近2个月中户卖出金额与近1年均值之差
    =====>>>> 25.75 0.03 424.0854305979047 2401.3727261643376 fc_T1_20240321_9，xbc_20240103_12 0.6363，0.5216
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df