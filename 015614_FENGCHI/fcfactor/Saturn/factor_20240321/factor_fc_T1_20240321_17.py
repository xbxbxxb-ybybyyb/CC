# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240321_17(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['BUY_VOLUME_LARGE_ORDER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['BUY_VOLUME_LARGE_ORDER'].unstack().rolling(1, min_periods=1).mean().stack()
    a = md_data['BUY_VOLUME_LARGE_ORDER'].unstack().rolling(10, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    前日大户买入总量(仅主动)相对于近2周的比值
    =====>>>> 17.542 0.027 41156.47744083659 82273.98017848699 xly_newsat_md10，wd_lzo_near_max_pct_bid 0.6847，0.5693
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df