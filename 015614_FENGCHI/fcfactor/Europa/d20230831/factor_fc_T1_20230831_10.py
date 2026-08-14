# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20230831_10(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -20)[0])
    amt = IO.read_data([start_date_, end_date], alt='/data/group/800463/data/generalStrong/minute5/amt.h5')
    vol = IO.read_data([start_date_, end_date], alt='/data/group/800463/data/generalStrong/minute5/volume.h5')
    high = IO.read_data([start_date_, end_date], alt='/data/group/800463/data/generalStrong/minute5/high.h5')
    low = IO.read_data([start_date_, end_date], alt='/data/group/800463/data/generalStrong/minute5/low.h5')
    vwap = amt / vol

    res = ((high - low) / vwap - 1).mean(axis=1) * 100

    res = pd.DataFrame(res.unstack().rolling(8, 2).mean().stack())
    res.columns = [factor_name]
    factor_df = res
    # -----------------------------------------------------日频相对于vwap的上下限的差值---------------------------------------------------------------
    """
    25.125 0.0479
    """
    return factor_df


