# coding: utf-8
# Author：fengchi863
# Date ：2023/7/4 20:52

import pandas as pd
from xquant.factordata import FactorData
import numpy as np
s = FactorData()

def calc_mdd(_s):
    mdd = (np.maximum.accumulate(np.nancumsum(_s)) - np.nancumsum(_s)).max()
    return -mdd

def factor_fc_nextT1_20231221_25(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['MONEYFLOW_PCT_VALUE'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['MONEYFLOW_PCT_VALUE'].unstack().rolling(2, min_periods=1).median().stack()
    a = md_data['MONEYFLOW_PCT_VALUE'].unstack().rolling(5, min_periods=1).median().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # ---------------------------------------------------------------------------------------------------------------------
    """
    当日资金净流入金额/流通市值长短期med差值
    13.416 0.0419 
    =====>>>> 13.416666666666668 0.041904694331990795 -0.002046197747090298 0.012696404869890389 fc_nextT1_20231214_5，fc_nextT1_20231207_33 0.6414，0.5193
    """
    return factor_df