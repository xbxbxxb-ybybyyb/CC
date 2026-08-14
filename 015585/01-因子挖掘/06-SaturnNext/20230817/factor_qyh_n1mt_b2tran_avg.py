# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
#
# 1min委买/成交的均值
# 32,0.079
# 和其他提交高相关
def factor_qyh_n1mt_b2tran_avg(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mt_b2tran_avg'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 130}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    # pre = tick_df['pre_close'].max()
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['b2tran'] = (tick_df['buy_amt'])/(tick_df['ValueTrade']+1000)
    res = tick_df['b2tran'].mean()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)