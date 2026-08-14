# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 净挂买/tick成交额最小值在活跃/不活跃的差异
# 26,0.032
#
def factor_qyh_n1mtick_20231130_2(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231130_2'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    # pre = tick_df['pre_close'].max()
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df1 = tick_df[tick_df['ValueTrade'] >= tick_df['ValueTrade'].quantile(0.75)]
    tick_df2 = tick_df[tick_df['ValueTrade'] <= tick_df['ValueTrade'].quantile(0.25)]
    #
    tick_df1 = tick_df1[tick_df1['ValueTrade'] > 0]
    tick_df1['cleanb2tran'] = (tick_df1['buy_amt'] - tick_df1['sell_amt'])/(tick_df1['ValueTrade'])
    tick_df2 = tick_df2[tick_df2['ValueTrade'] > 0]
    tick_df2['cleanb2tran'] = (tick_df2['buy_amt'] - tick_df2['sell_amt'])/(tick_df2['ValueTrade'])
    #
    res1 = tick_df1['cleanb2tran'].min()
    res2 = tick_df2['cleanb2tran'].min()
    res = res2-res1
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)