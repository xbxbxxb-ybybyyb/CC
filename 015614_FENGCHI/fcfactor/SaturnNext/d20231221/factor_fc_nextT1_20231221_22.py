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

def factor_fc_nextT1_20231221_22(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['BUY_VOLUME_EXLARGE_ORDER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['BUY_VOLUME_EXLARGE_ORDER'].unstack().rolling(6, min_periods=1).median().stack()
    a = md_data['BUY_VOLUME_EXLARGE_ORDER'].unstack().rolling(90, min_periods=1).median().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    当日机构买入总手数，近1周与近90天中位值之差
    22.75 -0.0587
    =====>>>> 22.75 -0.05870756335953518 27383.336938550143 104564.07979706925 fc_nextT1_20231130_16，fc_nextT1_20231130_3 0.6928，0.6919
    """
    return factor_df