# coding: utf-8
# Author：fengchi863
# Date ：2023/7/4 20:52

import pandas as pd
from xquant.factordata import FactorData
import numpy as np
s = FactorData()

def calc_mdd(_s):
    mdd = (np.maximum.accumulate(np.nancumsum(_s)) - np.nancumsum(_s)).max()
    return -mdd

def factor_fc_nextT1_20231207_25(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['S_MFD_INFLOW_LARGE_ORDER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['S_MFD_INFLOW_LARGE_ORDER'].unstack().rolling(6, min_periods=1).mean().stack()
    a = md_data['S_MFD_INFLOW_LARGE_ORDER'].unstack().rolling(10, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    机构买入金额+大户买入金额-(机构卖出金额+大户卖出金额)，近1周与近2周均值之差
    14.333 0.0266
    =====>>>> 14.333333333333334 0.026684721064587365 90.37123320417486 1447.7681650029456 xly_t_1_md_tz147，skk_pct_nixu10 0.3698，0.2969
    """
    return factor_df