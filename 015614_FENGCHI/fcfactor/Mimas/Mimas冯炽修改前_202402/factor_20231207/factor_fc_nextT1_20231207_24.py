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

def factor_fc_nextT1_20231207_24(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['S_MFD_INFLOW_OPEN'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['S_MFD_INFLOW_OPEN'].unstack().rolling(2, min_periods=1).mean().stack()
    a = md_data['S_MFD_INFLOW_OPEN'].unstack().rolling(40, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    10点前的资金净流入金额，近2日与近2个月的均值之差
    16.2916 0.03947 
    =====>>>> 16.291666666666668 0.039471461147171524 212.31335062908042 3581.148312024582 xly_t_1_md_tz150，saturn_Lzt_pj2r_bzt_ppnpa_std 0.3136，0.2939
    """
    return factor_df