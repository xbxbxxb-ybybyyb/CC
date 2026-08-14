# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240509_2(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['SELL_VALUE_MED_ORDER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['SELL_VALUE_MED_ORDER'].unstack().rolling(2, min_periods=1).mean().stack()
    a = md_data['SELL_VALUE_MED_ORDER'].unstack().rolling(120, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    近2日中单卖出金额与近半年均值的差异
    =====>>>> 25.0 0.015 5070.816224476829 10171.41611306971 fc_T1_20240321_7，wd_lzo_near_ul_bid_amt 0.6647，0.6317
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df