# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240411_3(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['OPEN_NET_INFLOW_RATE_VALUE_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['OPEN_NET_INFLOW_RATE_VALUE_L'].unstack().rolling(6, min_periods=1).mean().stack()
    a = md_data['OPEN_NET_INFLOW_RATE_VALUE_L'].unstack().rolling(240, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    开盘主力净流入率(金额)，近1周相对于近1年的差值
    =====>>>> 25.333 -0.058 0.7219213739187503 4.476542154420389 fc_T1_20240328_12，xbc_20240328_5 0.687，0.3936
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df