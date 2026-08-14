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

def factor_fc_nextT1_20231207_30(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['S_MFD_INFLOW_OPEN_LARGE_ORDER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['S_MFD_INFLOW_OPEN_LARGE_ORDER'].unstack().rolling(1, min_periods=1).mean().stack()
    a = md_data['S_MFD_INFLOW_OPEN_LARGE_ORDER'].unstack().rolling(120, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    10点前的大单净流入金额，昨日与近半年的均值对应增量
    12.5416 0.030
    =====>>>> 12.541666666666668 0.03051345788936319 -3736.9263209806873 6720.141560657873 fc_nextT1_20230817_4，fc_nextT1_20230803_2 0.691，0.6025
    """
    return factor_df