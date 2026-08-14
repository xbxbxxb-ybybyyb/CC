# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240321_10(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['BUY_VALUE_EXLARGE_ORDER_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['BUY_VALUE_EXLARGE_ORDER_ACT'].unstack().rolling(3, min_periods=1).mean().stack()
    a = md_data['BUY_VALUE_EXLARGE_ORDER_ACT'].unstack().rolling(10, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    当日机构买入金额(仅主动)，近3日相对于近两周的比值
    =====>>>> 13.5 0.033 1524.4665349529002 4098.969950696409 xly_newsat_md10，wd_lzo_near_ul_bid_amt 0.6875，0.6622
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df