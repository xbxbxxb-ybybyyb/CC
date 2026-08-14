# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20230921_12(start_date, end_date, IO, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['MONEYFLOW_PCT_VALUE_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['MONEYFLOW_PCT_VALUE_L'].unstack().rolling(6, min_periods=1).mean().stack() * 100
    a = md_data['MONEYFLOW_PCT_VALUE_L'].unstack().rolling(240, min_periods=1).mean().stack() * 100

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    大单净流入量/流通股数，近一周相对于过去一年均值的差值
    18.291666666666668 -0.045160426073867097 2.460667952949686 57.33457197882377 skk_roll_pdown_8_new，sundc_t_1_mf_8 0.3631，0.3266
    18.29 -0.045
    """
    return factor_df


