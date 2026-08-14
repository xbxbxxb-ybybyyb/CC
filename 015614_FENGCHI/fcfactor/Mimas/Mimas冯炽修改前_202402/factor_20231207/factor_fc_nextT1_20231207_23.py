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

def factor_fc_nextT1_20231207_23(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['S_MFD_INFLOW_CLOSEVOLUME_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['S_MFD_INFLOW_CLOSEVOLUME_L'].unstack().rolling(2, min_periods=1).mean().stack()
    a = md_data['S_MFD_INFLOW_CLOSEVOLUME_L'].unstack().rolling(20, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    14:30后的大单净流入量，近2日与近1个月的均值之差
    17.416 0.0203 
    =====>>>> 17.416666666666668 0.02036756314037758 1590.7266205040357 11234.606922645646 skk_v2c_mean，saturn_Lzt_pj2r_bzt_ppnpa_std 0.4087，0.2684
    """
    return factor_df