# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20231012_2(start_date, end_date, IO, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['S_MFD_INFLOWVOLUME'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['S_MFD_INFLOWVOLUME'].unstack().rolling(2, min_periods=1).mean().stack() * 100
    a = md_data['S_MFD_INFLOWVOLUME'].unstack().rolling(20, min_periods=1).mean().stack() * 100

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    最近2天 当日买入总量-当日卖出总量，即净买入量，相对于近20天以来的差值
    19.125 -0.05694
    =====>>>> 19.125 -0.05694116992013915 -127144.42703657431 6041653.398763567 fc_T1_20230921_14，fc_T1_20230928_4，xbc_20230921_3 0.7455，0.4856，0.4669
    """
    return factor_df


