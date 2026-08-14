# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20230831_9(start_date, end_date, IO, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -20)[0])
    amt = IO.read_data([start_date_, end_date], alt='/data/group/800463/data/generalStrong/minute5/amt.h5')
    vol = IO.read_data([start_date_, end_date], alt='/data/group/800463/data/generalStrong/minute5/volume.h5')
    opn = IO.read_data([start_date_, end_date], alt='/data/group/800463/data/generalStrong/minute5/open.h5')
    vwap = amt / vol

    res = (opn / vwap - 1).mean(axis=1) * 100

    res = pd.DataFrame(res.unstack().rolling(3, 2).mean().stack())
    res.columns = [factor_name]
    factor_df = res
    # -----------------------------------------------------开盘价相对于vwap的涨跌幅---------------------------------------------------------------
    """
    14.375 0.043
    """
    return factor_df


