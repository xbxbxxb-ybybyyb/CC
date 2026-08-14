# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 1min里成交金额的最小值
# -0.07,31
# next_pj2_number_buy_orders:28
def factor_qyh_n1mt_a_min(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mt_a_min'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 15108}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    # pre = tick_df['pre_close'].max()
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    length = len(tick_df[tick_df['ValueTrade'] == 0])
    tick_df = tick_df[tick_df['ValueTrade'] > 0]
    res = tick_df['ValueTrade'].min() / (length+1)
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)