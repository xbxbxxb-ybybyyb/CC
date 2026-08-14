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

def factor_fc_nextT1_20231229_6(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['VOLUME_DIFF_INSTITUTE_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['VOLUME_DIFF_INSTITUTE_ACT'].unstack().rolling(2, min_periods=1).median().stack()
    a = md_data['VOLUME_DIFF_INSTITUTE_ACT'].unstack().rolling(240, min_periods=1).median().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    特大单主动买量-特大单主动卖量，昨日均值与近1年中位值之差
    14.75 0.0367
    =====>>>> 14.750000000000002 0.03671487058440993 -1451.4398720107745 50394.890977270756 fc_nextT1_20230921_11，fc_nextT1_20231214_4 0.4703，0.4643
    """
    return factor_df