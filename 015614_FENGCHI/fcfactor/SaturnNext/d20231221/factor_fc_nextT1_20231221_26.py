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

def factor_fc_nextT1_20231221_26(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['NET_INFLOW_RATE_VOLUME_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['NET_INFLOW_RATE_VOLUME_L'].unstack().rolling(10, min_periods=1).median().stack()
    a = md_data['NET_INFLOW_RATE_VOLUME_L'].unstack().rolling(90, min_periods=1).median().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    大单净流入量/成交股数，长短期中位数之差
    12.791 -0.0343
    =====>>>> 12.791666666666668 -0.034346388943355774 0.5569580311365554 5.868070519825196 skk_20231207_28，skk_20231214_6 0.358，0.3502
    """
    return factor_df