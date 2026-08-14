# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240411_8(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['OPEN_NET_INFLOW_RATE_VOLUME'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['OPEN_NET_INFLOW_RATE_VOLUME'].unstack().rolling(2, min_periods=1).mean().stack()
    a = md_data['OPEN_NET_INFLOW_RATE_VOLUME'].unstack().rolling(3, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    10点前的资金净流入量/10点前的成交股数，近2日均值相对于近3日均值的差值
    =====>>>> 17.333 0.046 0.014497961425484897 0.08288145127608171 fc_T1_20240328_10，fc_T1_20240328_5 0.4625，0.4326
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df