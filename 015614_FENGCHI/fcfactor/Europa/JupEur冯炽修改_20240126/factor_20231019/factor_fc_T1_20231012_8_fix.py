# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20231012_8_fix(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['S_MFD_INFLOW_CLOSEVOLUME'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['S_MFD_INFLOW_CLOSEVOLUME'].unstack().rolling(2, min_periods=1).mean().stack() / 10
    a = md_data['S_MFD_INFLOW_CLOSEVOLUME'].unstack().rolling(3, min_periods=1).mean().stack() / 10

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    最近2天尾盘净流入量，相对于近3天尾盘净流入量的差值
    16.08 -0.042
    =====>>>> 16.083333333333332 -0.04199409998781705 -10.228.51023497938 779.253.3376335609 fc_T1_20230907_13，wj_last20_ls_actmoneyflow_diff 0.6434，0.5931
    """
    return factor_df


