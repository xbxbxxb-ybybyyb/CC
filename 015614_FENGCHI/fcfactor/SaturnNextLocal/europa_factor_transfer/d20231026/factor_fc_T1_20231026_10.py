# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20231026_10(start_date, end_date, IO, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['VALUE_DIFF_SMALL_TRADER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['VALUE_DIFF_SMALL_TRADER'].unstack().rolling(3, min_periods=1).mean().stack() / 100
    a = md_data['VALUE_DIFF_SMALL_TRADER'].unstack().rolling(240, min_periods=1).mean().stack() / 100

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    最近3天小单买额-小单卖额，即净买入额，相对于最近一年以来的差值
    16.33 0.043
    =====>>>> 16.333333333333336 0.04345334505072428 -0.9973623552064556 27.222977092861516 xly_t_1_tb47，skk_prs_rmin 0.6375，0.4515
    """
    return factor_df


