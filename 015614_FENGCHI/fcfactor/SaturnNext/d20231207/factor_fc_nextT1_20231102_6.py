# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_nextT1_20231102_6(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['VOLUME_DIFF_SMALL_TRADER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['VOLUME_DIFF_SMALL_TRADER'].unstack().rolling(2, min_periods=1).mean().stack() / 100
    a = md_data['VOLUME_DIFF_SMALL_TRADER'].unstack().rolling(240, min_periods=1).mean().stack() / 100

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    近两日小单买量-小单卖量，即散户量差，相对于近1年以来的差值
    24.4166 -0.0700  
    =====>>>> 24.41666666666667 -0.07007220248007907 28.205270304813354 398.45664209512614 sss_smallflow_s2_5_s，xly_t_1_md_tz147 0.5603，0.5336
    """
    return factor_df


