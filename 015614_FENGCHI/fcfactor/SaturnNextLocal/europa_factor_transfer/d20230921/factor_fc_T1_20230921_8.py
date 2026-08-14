# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20230921_8(start_date, end_date, IO, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['MONEYFLOW_PCT_VALUE'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['MONEYFLOW_PCT_VALUE'].unstack().rolling(1, min_periods=1).mean().stack() * 100
    a = md_data['MONEYFLOW_PCT_VALUE'].unstack().rolling(10, min_periods=1).mean().stack() * 100

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    当日资金主动净流入金额/流通市值 相对于过去10日差值
    26.58 -0.05
    26.583333333333336 -0.052669078246384504 -0.11413487520620266 1.7153245057557314 zwh_20230907_002，wj_last_C2preC_pct 0.5248，0.508
    !!!! fc_T1_20230921_15 0.8952059231949282
    """
    return factor_df


