# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def factor_qyh_n1mtick_20231207_14(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231207_14'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    #
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    #
    tick_df1 = tick_df[tick_df['ValueTrade'] >= tick_df['ValueTrade'].quantile(0.75)]
    tick_df1 = tick_df1.head(int(len(tick_df1)/2)) if len(tick_df1)>10 else tick_df1
    tick_df2 = tick_df[tick_df['ValueTrade'] <= tick_df['ValueTrade'].quantile(0.25)]
    tick_df2 = tick_df2.head(int(len(tick_df2)/2)) if len(tick_df2)>10 else tick_df2
    #
    tick_df1['factor'] = (tick_df1['buy_amt'] - tick_df1['sell_amt'])/(tick_df1['ValueTrade']+1)
    tick_df2['factor'] = (tick_df2['buy_amt'] - tick_df2['sell_amt'])/(tick_df2['ValueTrade']+1)
    #
    res1 = tick_df1['factor'].tail(1).mean() if not tick_df1.empty else np.nan
    res2 = tick_df2['factor'].tail(1).mean() if not tick_df2.empty else np.nan

    factor_dict = {factor_name: res2-res1}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)