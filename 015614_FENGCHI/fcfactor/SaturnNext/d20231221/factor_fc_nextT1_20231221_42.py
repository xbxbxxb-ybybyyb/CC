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

def factor_fc_nextT1_20231221_42(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['SELL_VOLUME_EXLARGE_ORDER_ACT'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['SELL_VOLUME_EXLARGE_ORDER_ACT'].unstack().rolling(3, min_periods=1).median().stack()
    a = md_data['SELL_VOLUME_EXLARGE_ORDER_ACT'].unstack().rolling(60, min_periods=1).median().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    当日机构主动卖出总量近3日与近3个月中位值之差
    21.5 -0.0575
    =====>>>> 21.5 -0.057546943650130515 291.91503272706956 932.6185365828709 fc_nextT1_20231130_16，wj_last20_diff 0.6864，0.6837
    """
    return factor_df