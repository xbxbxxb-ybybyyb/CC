# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240321_11(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['BUY_VALUE_MED_ORDER_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['BUY_VALUE_MED_ORDER_ACT'].unstack().rolling(1, min_periods=1).mean().stack()
    a = md_data['BUY_VALUE_MED_ORDER_ACT'].unstack().rolling(5, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    当日中户买入金额(仅主动)，前一日相对于过去一周的均值之比
    =====>>>> 20.792 0.061 1485.7999564564454 3128.048650195629 wj_last_actbig_ratio，wd_lzkcs_pct_sum_d_mean 0.565，0.5641
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df