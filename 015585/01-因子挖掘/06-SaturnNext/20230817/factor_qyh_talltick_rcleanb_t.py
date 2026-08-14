# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
#
# 净委买在尾盘的值
# gg 高相关
#
def factor_qyh_talltick_rcleanb_t(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_rcleanb_t'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.5}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    # pre = tick_df['pre_close'].max()
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['rcleanb'] = (tick_df['buy_amt'] - tick_df['sell_amt'])/(tick_df['buy_amt'] + tick_df['sell_amt'])
    #
    res = tick_df['rcleanb'].tail(1).values[0]
    if res == 1:
        res = tick_df[tick_df['rcleanb']<1]
        res = res['rcleanb'].tail(1).values[0] if not res.empty else 1
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)