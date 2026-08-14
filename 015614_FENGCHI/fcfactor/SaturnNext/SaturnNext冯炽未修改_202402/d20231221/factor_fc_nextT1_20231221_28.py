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

def factor_fc_nextT1_20231221_28(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['OPEN_MONEYFLOW_PCT_VOLUME_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['OPEN_MONEYFLOW_PCT_VOLUME_L'].unstack().rolling(3, min_periods=1).median().stack()
    a = md_data['OPEN_MONEYFLOW_PCT_VOLUME_L'].unstack().rolling(90, min_periods=1).median().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    10点前的大单净流入量用流通股放缩长短期中位值之差
    15.166 0.0403
    =====>>>> 15.166666666666668 0.04033813609465316 -0.12791252385763893 0.5688925871119211 fc_nextT1_20231207_13，fc_nextT1_20231207_19 0.4803，0.3929
    """
    return factor_df