# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20231102_6(start_date, end_date, IO, return_fillna_dic=False):
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
    32.08 0.0578
    =====>>>> 32.08333333333333 0.05786581471649759 -18.687971604427613 375.39811465410264 xly_t_1_tb47，skk_pct_mi2 0.5716，0.4882
    """
    return factor_df


