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

def factor_fc_nextT1_20231207_11(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['NET_INFLOW_RATE_VALUE_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['NET_INFLOW_RATE_VALUE_L'].unstack().rolling(10, min_periods=1).mean().stack()
    a = md_data['NET_INFLOW_RATE_VALUE_L'].unstack().rolling(240, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    大单净流入金额/成交金额，最近2周与最近1年均值之差
    15.583333333333334 -0.030052666886795917  
    =====>>>> 15.583333333333334 -0.030052666886795917 0.8057071209793236 7.341227991540399 skk_pct_t_mean，list_len 0.4674，0.4275
    """
    return factor_df