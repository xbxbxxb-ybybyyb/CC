# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def factor_qyh_talltick_rcleanb_p25_a25(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_rcleanb_p25_a25'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}

    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    # tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    p25 = tick_df['LastPx'].quantile(0.25)
    tick_df = tick_df[tick_df['ValueTrade'] <= tick_df['ValueTrade'].quantile(0.25)]
    tick_df = tick_df[tick_df['LastPx'] < p25]
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['rcleanb'] = (tick_df['buy_amt'] - tick_df['sell_amt']) / (tick_df['buy_amt'] + tick_df['sell_amt'])
    res = tick_df['rcleanb'].min()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)