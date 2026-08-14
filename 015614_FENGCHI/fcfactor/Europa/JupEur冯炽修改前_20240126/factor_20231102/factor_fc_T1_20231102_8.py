# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20231102_8(start_date, end_date, IO, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['VOLUME_DIFF_SMALL_TRADER'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['VOLUME_DIFF_SMALL_TRADER'].unstack().rolling(6, min_periods=1).mean().stack() / 100
    a = md_data['VOLUME_DIFF_SMALL_TRADER'].unstack().rolling(240, min_periods=1).mean().stack() / 100

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    近一周散户量差相对于近1年的增量
    29.08 0.0517
    =====>>>> 29.083333333333336 0.05170211846078301 0.07748670166243578 188.59590012251346 xly_t_1_tb47，skk_pct_RKS_mi7 0.5254，0.4542
    """
    return factor_df


