# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240321_18(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['BUY_VOLUME_EXLARGE_ORDER_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['BUY_VOLUME_EXLARGE_ORDER_ACT'].unstack().rolling(20, min_periods=1).mean().stack()
    a = md_data['BUY_VOLUME_EXLARGE_ORDER_ACT'].unstack().rolling(120, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    最近1月机构买入总量(仅主动)相对于近半年均值的比值
    =====>>>> 15.667 0.011 48.31591447150776 262.9402133459542 xbc_20240103_12，qyh_sat_md_20240111_6 0.637，0.4885
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df