# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def factor_qyh_talltick_rcleanb_p25_tail(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_rcleanb_p25_tail'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['LastPx'] < tick_df['LastPx'].quantile(0.25)]
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['rcleanb'] = (tick_df['buy_amt'] - tick_df['sell_amt']) / (tick_df['buy_amt'] + tick_df['sell_amt'])
    res = tick_df['rcleanb'].tail(1).values[0] if len(tick_df) > 0 else np.nan
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)