# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20231012_4_fix(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['S_MFD_INFLOWVOLUME_LARGE_ORDER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['S_MFD_INFLOWVOLUME_LARGE_ORDER'].unstack().rolling(30, min_periods=1).mean().stack() / 10
    a = md_data['S_MFD_INFLOWVOLUME_LARGE_ORDER'].unstack().rolling(240, min_periods=1).mean().stack() / 10

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    最近1个月大单净流入量，相对于近一年以来大单净流入量的差值
    18.708 -0.039
    =====>>>> 18.708333333333336 -0.039937790021562926 -30.861.615522271673 1200.273.5571227146 xbc_high_pct_chg_turn_max，mf_dm_ms_ds_mean20 0.3461，0.3147
    """
    return factor_df


