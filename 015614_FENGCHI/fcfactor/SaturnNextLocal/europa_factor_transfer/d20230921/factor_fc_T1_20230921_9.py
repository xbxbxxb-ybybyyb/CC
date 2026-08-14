# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20230921_9(start_date, end_date, IO, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['CLOSE_NET_INFLOW_RATE_VALUE'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['CLOSE_NET_INFLOW_RATE_VALUE'].unstack().rolling(6, min_periods=1).mean().stack() * 100
    a = md_data['CLOSE_NET_INFLOW_RATE_VALUE'].unstack().rolling(120, min_periods=1).mean().stack() * 100

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    最近1周尾盘资金流入率，相对于近半年以来尾盘资金流入率的差值
    23.875 -0.038
    23.875 -0.038015934341054734 0.09645563812918712 2.2722091871040115 xly_t_1_tx35，skk_v2c_mean 0.4991，0.3055
    """
    return factor_df


