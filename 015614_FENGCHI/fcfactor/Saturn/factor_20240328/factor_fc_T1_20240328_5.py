# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240328_5(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['MONEYFLOW_PCT_VALUE'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['MONEYFLOW_PCT_VALUE'].unstack().rolling(2, min_periods=1).mean().stack()
    a = md_data['MONEYFLOW_PCT_VALUE'].unstack().rolling(3, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    近2日净主动买入额占比相对于近3日差值
    =====>>>> 23.458 0.063 -0.000268242177068919 0.0066598595232947155 fc_LastZtLastTrans_20240314_5，Institute_earn 0.5781，0.4511
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df