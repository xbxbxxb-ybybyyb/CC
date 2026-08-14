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

def factor_fc_nextT1_20231207_20(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['S_MFD_INFLOW'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['S_MFD_INFLOW'].unstack().rolling(2, min_periods=1).mean().stack()
    a = md_data['S_MFD_INFLOW'].unstack().rolling(5, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    当日主动买入总额-当日主动卖出总额，近2日与近1周均值之差
    15.16 0.0387
    =====>>>> 15.166666666666668 0.03874999500257823 -112.29975643307901 4724.37399893913 xly_t_1_md_tz150，saturn_Lzt_pj2r_bzt_ppnpa_std 0.376，0.3468
    """
    return factor_df