# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def factor_qyh_talltick_rcleanb_20_h2t(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_rcleanb_20_h2t'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.21}

    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['rcleanb'] = (tick_df['buy_amt'] - tick_df['sell_amt'])/(tick_df['buy_amt'] + tick_df['sell_amt'])
    #
    res = tick_df.head(20)['rcleanb'].min() - tick_df.tail(20)['rcleanb'].min()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的fDataFrame中列名也为因子名称;
    # 以上的四个因子名称应该统一。

