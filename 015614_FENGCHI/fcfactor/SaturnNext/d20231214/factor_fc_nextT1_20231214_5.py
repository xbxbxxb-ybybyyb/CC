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

def factor_fc_nextT1_20231214_5(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['VOLUME_DIFF_LARGE_TRADER_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['VOLUME_DIFF_LARGE_TRADER_ACT'].unstack().rolling(2, min_periods=1).mean().stack()
    a = md_data['VOLUME_DIFF_LARGE_TRADER_ACT'].unstack().rolling(5, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    大单主动买量-大单主动卖量，近2日均值占近1周均值的比例
    15.583 0.0382
    =====>>>> 15.583333333333336 0.03823978513065425 -892.9320260716862 49868.48345182367 fc_nextT1_20230921_11，fc_nextT1_20231207_19 0.4678，0.4417
    """
    return factor_df