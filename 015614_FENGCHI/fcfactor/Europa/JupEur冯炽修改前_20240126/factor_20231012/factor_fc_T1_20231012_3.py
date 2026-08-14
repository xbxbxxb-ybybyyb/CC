# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_T1_20231012_3(start_date, end_date, IO, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['S_MFD_INFLOW_CLOSEVOLUME'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['S_MFD_INFLOW_CLOSEVOLUME'].unstack().rolling(6, min_periods=1).mean().stack() * 100
    a = md_data['S_MFD_INFLOW_CLOSEVOLUME'].unstack().rolling(120, min_periods=1).mean().stack() * 100

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    最近1周尾盘净流入量，相对于近半年以来尾盘净流入量的差值
    18.91 -0.043
    =====>>>> 18.916666666666668 -0.04374971789305219 -35900.5320145346 790783.207603495 xly_t_1_tx35，wj_last20_ls_actmoneyflow_diff 0.5527，0.366
    """
    return factor_df


