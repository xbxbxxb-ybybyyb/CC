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

def factor_fc_nextT1_20231207_28(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['VALUE_DIFF_INSTITUTE_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['VALUE_DIFF_INSTITUTE_ACT'].unstack().rolling(2, min_periods=1).mean().stack()
    a = md_data['VALUE_DIFF_INSTITUTE_ACT'].unstack().rolling(10, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    特大单主动买额-特大单主动卖额，近2日与近2周均值之差
    14.75 0.038
    =====>>>> 14.75 0.03855348114996247 49.07407764501039 4032.623976619546 saturn_Lzt_pj2r_bzt_ppnpa_std，saturn_lztb_qyh_TTra_ratio_small_b2s_std 0.3323，0.3275
    """
    return factor_df