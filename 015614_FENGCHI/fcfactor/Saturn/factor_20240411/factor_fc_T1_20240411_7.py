# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240411_7(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['OPEN_MONEYFLOW_PCT_VALUE'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['OPEN_MONEYFLOW_PCT_VALUE'].unstack().rolling(3, min_periods=1).mean().stack()
    a = md_data['OPEN_MONEYFLOW_PCT_VALUE'].unstack().rolling(20, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    10点前的资金主动净流入金额/流通市值，近3日均值相对于近1个月差值
    =====>>>> 18.792 0.049 -1.0441670718948335e-05 0.006072548787365839 fc_T1_20240328_10，wj_last_openamt，wj_last_StartEndMoney_diff 0.7645，0.5606，0.5045
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df