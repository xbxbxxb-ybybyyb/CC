# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240328_13(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['NET_INFLOW_RATE_VALUE'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['NET_INFLOW_RATE_VALUE'].unstack().rolling(3, min_periods=1).mean().stack()
    a = md_data['NET_INFLOW_RATE_VALUE'].unstack().rolling(5, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    近3日净流入率（当日净流入/成交额），相对于近1周的均值
    =====>>>> 13.5 0.045 -0.0004624456218289608 0.07129259502237623 fc_LastZtLastTrans_20240314_5，yzhan_hf_s2_57 0.4203，0.3215
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df