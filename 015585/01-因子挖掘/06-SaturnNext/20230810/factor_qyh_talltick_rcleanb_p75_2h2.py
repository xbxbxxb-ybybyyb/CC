# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
#
# 净委买在价格较高时与尾盘时的差
# res1: 1542的标准差; res2:4,-0.03,775
#
#
def factor_qyh_talltick_rcleanb_p75_2h2(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_rcleanb_p75_2h2'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    # pre = tick_df['pre_close'].max()
    # tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['rcleanb'] = (tick_df['buy_amt'] - tick_df['sell_amt'])/(tick_df['buy_amt'] + tick_df['sell_amt'])
    #
    tick_df1 = tick_df[tick_df['LastPx'] > tick_df['LastPx'].quantile(0.75)]
    tick_df2 = tick_df[tick_df['LastPx'] < tick_df['LastPx'].quantile(0.25)]
    tick_df1 = tick_df1.head(20)
    tick_df2 = tick_df2.head(20)
    res1 = (tick_df1['rcleanb']**2).sum() / (tick_df1['rcleanb'].sum()**2) if abs(tick_df1['rcleanb'].sum()) > 0.001 else np.nan
    res2 = (tick_df2['rcleanb']**2).sum() / (tick_df2['rcleanb'].sum()**2)
    factor_dict = {factor_name: res1 - res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)