# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20230907_13(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['CLOSE_MONEYFLOW_PCT_VALUE'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['CLOSE_MONEYFLOW_PCT_VALUE'].unstack().rolling(2, min_periods=1).mean().stack()
    a = md_data['CLOSE_MONEYFLOW_PCT_VALUE'].unstack().rolling(5, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    尾盘资金净流入金额长短期差值
    25.54 -0.06024
    """
    return factor_df


