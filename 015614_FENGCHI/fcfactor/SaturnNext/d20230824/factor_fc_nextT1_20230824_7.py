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

def factor_fc_nextT1_20230824_7(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -20)[0])
    amt = IO.read_data([start_date_, end_date], alt='/data/group/800463/data/generalStrong/minute5/amt.h5')
    vol = IO.read_data([start_date_, end_date], alt='/data/group/800463/data/generalStrong/minute5/volume.h5')
    close = IO.read_data([start_date_, end_date], alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    vwap = amt / vol

    res = (close / vwap - 1).mean(axis=1) * 100

    res = pd.DataFrame(res.unstack().rolling(5, 2).mean().stack())
    res.columns = [factor_name]
    factor_df = res
    # ------------------------------------------------------五分钟频close与vwap的涨跌幅日内均值的5日均值---------------------------------------------------------------
    """
    17.041 -0.0356
    """
    return factor_df
"""
# minute5
open high low close amt vol
m925 m930 m935 ... m1130  m1300 m1305 ... m1430 m1435 ... m1455
表示的是这五分钟内的amt和vol，不是截至当前累积的
iloc[:, :25]就是上午
"""