# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 每个tick净委买/全天总成交额的均值
# 26,-0.05
def factor_qyh_talltick_cleanb2ttran(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_cleanb2ttran'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.04}
    # pre = tick_df['pre_close'].max()

    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    cleanb2ttran = ((tick_df['buy_amt'] - tick_df['sell_amt'])
                    /(tick_df['TotalValueTrade'].max())).mean()
    factor_dict = {factor_name: cleanb2ttran}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的fDataFrame中列名也为因子名称;
    # 以上的四个因子名称应该统一。

