# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20231019_7_fix(start_date, end_date, IO, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['S_MFD_INFLOWVOLUME'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['S_MFD_INFLOWVOLUME'].unstack().rolling(3, min_periods=1).mean().stack() / 10
    a = md_data['S_MFD_INFLOWVOLUME'].unstack().rolling(10, min_periods=1).mean().stack() / 10

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    最近3天 当日买入总量-当日卖出总量，即净买入量，相对于近10天以来的差值
    16.83 -0.04
    =====>>>> 16.833333333333336 -0.047366716553768756 -73.696.68975690912 4272.169.970409225 fc_T1_20230921_14，slxd 0.5988，0.3917
    !!!! fc_T1_20231012_2 0.6963158504693935
    """
    return factor_df


