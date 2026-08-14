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

def factor_fc_nextT1_20231229_4(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['VOLUME_DIFF_LARGE_TRADER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['VOLUME_DIFF_LARGE_TRADER'].unstack().rolling(3, min_periods=1).median().stack()
    a = md_data['VOLUME_DIFF_LARGE_TRADER'].unstack().rolling(20, min_periods=1).median().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    大单买量-大单卖量，3日中位值与近1个月中位值之差
    16.541 0.056
    =====>>>> 16.541666666666668 0.056035810036253395 -5953.391019984289 20358.325314936905 fc_nextT1_20231207_31，fc_nextT1_20231214_4 0.6489，0.5014
    """
    return factor_df