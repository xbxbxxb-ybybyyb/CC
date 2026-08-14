# coding: utf-8
# Author：fengchi863
# Date ：2023/3/27 18:50

import pandas as pd
from xquant.factordata import FactorData

s = FactorData()


def factor_fc_noise_10d(start_date, end_date, IO, return_fillna_dic=False):
    factor_name = 'fc_noise_10d'

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['MD']}
    # 计算全部股票在全部时间区间上的因子值，之后会在run_factor_demo函数中进行向后平移一天和样本的筛选
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -60)[0])  # 向前取的天数至少大于要用到的数据日期数+1天
    md_data = IO.read_data([start_date_, end_date], columns=['turn', 'open', 'close', 'adjfactor']
                           , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    close = md_data['close'] * md_data['adjfactor']
    opn = md_data['open'] * md_data['adjfactor']
    turn = md_data['turn']
    close = close.unstack()
    opn = opn.unstack()
    turn = turn.unstack()

    price_diff = (close - opn) / close
    price_diff_rank = price_diff.rank(pct=True, axis=1)
    price_diff_rank = pd.DataFrame(2 + price_diff_rank.values, index=price_diff.index, columns=price_diff.columns)

    turn_mean = turn.rolling(window=10).mean()
    turn_diff = (turn - turn_mean) / turn_mean
    turn_diff_rank = turn_diff.rank(pct=True, axis=1)
    turn_diff_rank = pd.DataFrame(1 + turn_diff_rank.values, index=turn_diff.index, columns=turn_diff.columns)

    factor = price_diff_rank * turn_diff_rank
    ret = factor.rolling(10).mean() / factor.rolling(10).std()
    ret = ret.loc[pd.to_datetime(str(start_date)):]

    factor_df = pd.DataFrame()
    factor_df[factor_name] = ret.stack()
    return factor_df