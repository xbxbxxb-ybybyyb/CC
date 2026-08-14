# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240321_16(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['BUY_VOLUME_MED_ORDER_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['BUY_VOLUME_MED_ORDER_ACT'].unstack().rolling(90, min_periods=1).mean().stack()
    a = md_data['BUY_VOLUME_MED_ORDER_ACT'].unstack().rolling(240, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    中户买入总量(仅主动)近3个月相对于近1年的比值
    =====>>>> 17.667 0.027 29.82082413408525 123.92003780330725 xbc_20240103_12，zwh_20240229_021 0.3984，0.3456
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df