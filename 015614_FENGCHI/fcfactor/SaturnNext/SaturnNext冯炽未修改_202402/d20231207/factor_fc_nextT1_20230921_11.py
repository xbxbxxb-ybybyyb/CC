# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_nextT1_20230921_11(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['AShareMoneyFlow']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['MONEYFLOW_PCT_VOLUME_L'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

    b = md_data['MONEYFLOW_PCT_VOLUME_L'].unstack().rolling(2, min_periods=1).mean().stack() * 100
    a = md_data['MONEYFLOW_PCT_VOLUME_L'].unstack().rolling(240, min_periods=1).mean().stack() * 100

    factor_df = pd.DataFrame()
    factor_df[factor_name] = b - a
    """
    大单净流入量/流通股数，近2日相对于过去一年均值的差值
    28.333 0.05863  
    =====>>>> 28.333333333333336 0.058631097935783326 4.071589637167385 115.9811875459633 fc_nextT1_20230817_4，xly_t_1_md_tz147 0.4821，0.4779
    """
    return factor_df


