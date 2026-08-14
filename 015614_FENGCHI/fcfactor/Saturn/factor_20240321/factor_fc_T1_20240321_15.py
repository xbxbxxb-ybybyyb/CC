# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240321_15(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['BUY_VOLUME_SMALL_ORDER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['BUY_VOLUME_SMALL_ORDER'].unstack().rolling(1, min_periods=1).mean().stack()
    a = md_data['BUY_VOLUME_SMALL_ORDER'].unstack().rolling(240, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    前日散户买入总量(仅主动)相对于近1年均值的比值
    =====>>>> 18.375 0.017 27702.04862771895 92028.07835774124 wd_lzkcs_pct_sum_d_mean，xbc_20240103_12 0.5754，0.5698
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df