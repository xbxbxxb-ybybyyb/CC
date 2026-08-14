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

def factor_fc_nextT1_20231207_37(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['VALUE_DIFF_SMALL_TRADER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['VALUE_DIFF_SMALL_TRADER'].unstack().rolling(6, min_periods=1).mean().stack()
    a = md_data['VALUE_DIFF_SMALL_TRADER'].unstack().rolling(120, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    小单买额-小单卖额，近6日与近半年的均值差值
    16.833 -0.04521
    =====>>>> 16.833333333333336 -0.045213474428281955 136.23754217388017 1929.0368458701807 fc_nextT1_20231130_2，fc_nextT1_20230817_4 0.4354，0.4301
    """
    return factor_df