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

def factor_fc_nextT1_20231207_13(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['OPEN_MONEYFLOW_PCT_VOLUME_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['OPEN_MONEYFLOW_PCT_VOLUME_L'].unstack().rolling(3, min_periods=1).mean().stack()
    a = md_data['OPEN_MONEYFLOW_PCT_VOLUME_L'].unstack().rolling(10, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    10点前的大单净流入量/流通股数近3日与近2周均值之差
    12.666666666666668 0.03636858516963281  
    =====>>>> 12.666666666666668 0.03636858516963281 -0.12225940396293815 0.40723938912416663 xly_t_1_md_tz178，fc_nextT1_20230817_4 0.4672，0.3742
    """
    return factor_df