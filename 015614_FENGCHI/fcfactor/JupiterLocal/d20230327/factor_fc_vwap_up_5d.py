# coding: utf-8
# Author：fengchi863
# Date ：2023/3/29 10:25

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()


def factor_fc_vwap_up_5d(start_date, end_date, IO, return_fillna_dic=False):
    factor_name='fc_vwap_up_5d'

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['minute5']}
    # 计算全部股票在全部时间区间上的因子值，之后会在run_factor_demo函数中进行向后平移一天和样本的筛选
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -30)[0])  # 向前取的天数至少大于要用到的数据日期数+1天
    minute_amt = IO.read_data([start_date_, end_date], alt='/data/group/800463/data/generalStrong/minute5/amt.h5')
    minute_close = IO.read_data([start_date_, end_date], alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    minute_volume = IO.read_data([start_date_, end_date], alt='/data/group/800463/data/generalStrong/minute5/volume.h5')
    minute_vwap = minute_amt.T.expanding().sum().T / minute_volume.T.expanding().sum().T

    up_flag = minute_close > minute_vwap
    daily_up_flag = up_flag.sum(axis=1)
    ret = daily_up_flag.unstack().rolling(5).sum().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = ret
    return factor_df