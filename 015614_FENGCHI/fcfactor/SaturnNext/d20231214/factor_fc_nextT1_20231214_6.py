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

def factor_fc_nextT1_20231214_6(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['VOLUME_DIFF_INSTITUTE_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['VOLUME_DIFF_INSTITUTE_ACT'].unstack().rolling(2, min_periods=1).mean().stack()
    a = md_data['VOLUME_DIFF_INSTITUTE_ACT'].unstack().rolling(240, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    特大单主动买量-特大单主动卖量，昨日与近1年均值的差值
    20.041 -0.0466
    =====>>>> 20.04166 -0.0466 1857.1643015004386 13261.020869246617 fc_nextT1_20231207_37，fc_nextT1_20231207_19 0.5234，0.5206
    """
    return factor_df