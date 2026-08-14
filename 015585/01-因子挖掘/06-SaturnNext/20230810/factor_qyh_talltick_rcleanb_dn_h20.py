# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
#
# 净委买在开始下跌时的值
#
#
def factor_qyh_talltick_rcleanb_dn_h20(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_rcleanb_dn_h20'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 65}
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
    tick_df1 = tick_df[tick_df['LastPx'] < tick_df['LastPx'].shift(1)]
    res = tick_df1.tail(100)['rcleanb'].mean() if len(tick_df1) > 100 else np.nan
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)