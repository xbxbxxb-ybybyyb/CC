# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20231026_11(start_date, end_date, IO, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['VOLUME_DIFF_SMALL_TRADER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['VOLUME_DIFF_SMALL_TRADER'].unstack().rolling(1, min_periods=1).mean().stack() / 100
    a = md_data['VOLUME_DIFF_SMALL_TRADER'].unstack().rolling(240, min_periods=1).mean().stack() / 100

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    当日小单买量-小单卖量，相对于最近一年以来的差异
    16.33 0.040
    =====>>>> 16.333333333333336 0.040354540527680886 -32.6789197474368 544.5899073555423 xbc_20230921_2，wj_last_C2preC_pct 0.5467，0.4886
    """
    return factor_df


