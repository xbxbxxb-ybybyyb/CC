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

def factor_fc_nextT1_20231207_19(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['S_MFD_INFLOWVOLUME_LARGE_ORDER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['S_MFD_INFLOWVOLUME_LARGE_ORDER'].unstack().rolling(3, min_periods=1).mean().stack()
    a = md_data['S_MFD_INFLOWVOLUME_LARGE_ORDER'].unstack().rolling(30, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    机构买入总量+大户买入总量-(机构卖出总量+大户卖出总量)，近3日与近30日均值之差
    22.958333333333336 0.05198748785578406  
    =====>>>> 22.958333333333336 0.05198748785578406 2587.0603913768527 39841.66159570507 xly_t_1_md_tz147，sss_smallflow_s2_5_s 0.5598，0.4258
    """
    return factor_df