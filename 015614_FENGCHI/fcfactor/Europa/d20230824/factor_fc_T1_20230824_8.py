# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20230824_8(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -130)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['S_MFD_INFLOW_CLOSEVOLUME_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    factor_df = pd.DataFrame()
    factor_df[factor_name] = md_data['S_MFD_INFLOW_CLOSEVOLUME_L'].unstack().diff().rolling(120, min_periods=1).mean().stack()
    # ------------------------------------------------------14:30后的大单净流入量日差值取平均-------------------------------------------------------------
    """
    样本内得分 16.83 -0.04492
    """
    return factor_df


