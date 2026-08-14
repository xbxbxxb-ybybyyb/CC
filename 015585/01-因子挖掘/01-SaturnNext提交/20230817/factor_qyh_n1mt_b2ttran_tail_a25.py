# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def factor_qyh_n1mt_b2ttran_tail_a25(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mt_b2ttran_tail_a25'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 40}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    # pre = tick_df['pre_close'].max()
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df1 = tick_df[tick_df['ValueTrade'] <= tick_df['ValueTrade'].quantile(0.25)]
    tick_df1['buy_amt'] = tick_df1['TotalBidQty'] * tick_df1['WeightedAvgBidPx']
    tick_df1['b2ttran'] = (tick_df1['buy_amt'])/(tick_df1['ValueTrade'].sum()+1)
    res = tick_df1['b2ttran'].tail(1).values[0] if not tick_df.empty else np.nan
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)