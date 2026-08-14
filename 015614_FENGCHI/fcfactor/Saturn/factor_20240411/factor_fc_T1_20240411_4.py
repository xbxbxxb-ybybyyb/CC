# coding: utf-8
# Author：fengchi863
# Date ：2024/3/20 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_T1_20240411_4(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['OPEN_NET_INFLOW_RATE_VALUE_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['OPEN_NET_INFLOW_RATE_VALUE_L'].unstack().rolling(1, min_periods=1).mean().stack()
    a = md_data['OPEN_NET_INFLOW_RATE_VALUE_L'].unstack().rolling(240, min_periods=1).mean().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    # -------------------------------------------------------------------------------------------------------------------
    """
    当日开盘主力净流入率，前一日zt日相对于近1年的差值
    =====>>>> 24.583 -0.033 5.141426839446511 10.808236672001597 wj_last_lflow_rate，wd_lzt_act_tdiff_mdm 0.5518，0.4814
    """
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df