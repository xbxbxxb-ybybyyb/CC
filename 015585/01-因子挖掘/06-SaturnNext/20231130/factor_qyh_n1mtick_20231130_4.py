# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 开盘1min里，委买/成交的末尾值在活跃/不活跃的差异
# 17,-0.063
#
def factor_qyh_n1mtick_20231130_4(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231130_4'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    # pre = tick_df['pre_close'].max()
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['b2tran'] = (tick_df['buy_amt'])/(tick_df['ValueTrade']+1e-3)
    tick_df = tick_df[tick_df['ValueTrade']>0]
    #
    tick_df1 = tick_df[tick_df['ValueTrade'] > tick_df['ValueTrade'].quantile(0.5)]
    tick_df2 = tick_df[tick_df['ValueTrade'] < tick_df['ValueTrade'].quantile(0.5)]
    res1 = tick_df1['b2tran'].tail(1).mean()
    res2 = tick_df2['b2tran'].tail(1).mean()
    res = res1 - res2
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)