# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240321_3(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['BUY_VALUE_EXLARGE_ORDER_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['BUY_VALUE_EXLARGE_ORDER_ACT'].unstack().rolling(2, min_periods=1).mean().stack()
    a = md_data['BUY_VALUE_EXLARGE_ORDER_ACT'].unstack().rolling(3, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------

    """
    当日机构主动买入金额，近3日差值
    =====>>>> 31.25 0.07 900.5965575807763 2384.587442402761 wd_lzo_near_ul_bid_amt，xly_newsat_md10 0.6404，0.6241
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df