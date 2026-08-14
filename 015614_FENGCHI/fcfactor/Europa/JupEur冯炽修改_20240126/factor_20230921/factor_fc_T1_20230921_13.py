# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20230921_13(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['CLOSE_NET_INFLOW_RATE_VALU_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['CLOSE_NET_INFLOW_RATE_VALU_L'].unstack().rolling(1, min_periods=1).mean().stack() * 100
    a = md_data['CLOSE_NET_INFLOW_RATE_VALU_L'].unstack().rolling(240, min_periods=1).mean().stack() * 100

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    大单尾盘资金流入率，大单净流入金额/成交金额，当日与最近1年的均值的差值
    18 -0.052
    18.0 -0.052906933211252935 21.90281736777541 327.46395410803524 fc_T1_20230831_2，wj_last2_moneyflow_endbig 0.6097，0.6071
    """
    return factor_df


