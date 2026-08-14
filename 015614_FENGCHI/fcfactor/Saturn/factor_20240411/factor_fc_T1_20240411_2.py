# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240411_2(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['OPEN_NET_INFLOW_RATE_VALUE'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['OPEN_NET_INFLOW_RATE_VALUE'].unstack().rolling(2, min_periods=1).mean().stack()
    a = md_data['OPEN_NET_INFLOW_RATE_VALUE'].unstack().rolling(120, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    10点前的资金净流入金额/10点前的成交额，近2日表现相对于近半年差值
    =====>>>> 25.917 0.047 0.05395406918393508 0.17226809704706558 fc_T1_20240328_10，wj_last_openamt 0.6761，0.6295
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df