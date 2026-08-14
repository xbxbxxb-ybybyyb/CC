# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20230831_3(start_date, end_date, IO, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -130)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['MONEYFLOW_PCT_VALUE'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    factor_df = pd.DataFrame()
    factor_df[factor_name] = md_data['MONEYFLOW_PCT_VALUE'].unstack().diff().rolling(40, min_periods=1).mean().stack()
    # ----------------------------------------------------------当日资金主动部分净流入金额/流通市值---------------------------------------------------------
    """
    样本内得分 15.58 -0.039
    """
    return factor_df


