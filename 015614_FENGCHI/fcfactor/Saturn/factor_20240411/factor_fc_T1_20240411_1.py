# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240411_1(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['OPEN_MONEYFLOW_PCT_VOLUME'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['OPEN_MONEYFLOW_PCT_VOLUME'].unstack().rolling(1, min_periods=1).mean().stack()
    a = md_data['OPEN_MONEYFLOW_PCT_VOLUME'].unstack().rolling(2, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    10点前的资金净流入量/流通股本，近两日之差
    =====>>>> 26.792 0.054 0.06487303000509817 0.8349735155276317 fc_T1_20240328_9，wj_last_openamt，wj_last_StartEndMoney_diff 0.9994，0.6766，0.601
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df