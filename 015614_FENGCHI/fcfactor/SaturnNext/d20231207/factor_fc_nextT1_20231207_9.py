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

def factor_fc_nextT1_20231207_9(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['NET_INFLOW_RATE_VOLUME_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['NET_INFLOW_RATE_VOLUME_L'].unstack().rolling(3, min_periods=1).mean().stack()
    a = md_data['NET_INFLOW_RATE_VOLUME_L'].unstack().rolling(10, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    大单净流入量/成交股数，近3日与近2周均值之差
    25.125 0.0474
    =====>>>> 25.125 0.04745113026212046 3.095889561496107 6.376221784294027 saturn_wd_mf_bvs_d_svs，xly_t_1_md_tz147 0.4177，0.3927
    """
    return factor_df