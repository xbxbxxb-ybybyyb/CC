# coding: utf-8
# Author：fengchi863
# Date ：2023/4/27 11:16

import pandas as pd
import datetime as dt

def factor_fc_last_buy_turn(df, return_fillna_dic=False):
    factor_name = 'fc_last_buy_turn'

    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    ff_shares = df['ff_shares'].iloc[0]
    df = df[df['TradeMoney'] > 0]
    df['buy_flag'] = (df['TradeBuyNo'] > df['TradeSellNo']).astype(float)
    df = df[df['MDTime'] >= 93000000]

    sell_df = df[df['buy_flag'] == 0]
    group_sell_df = sell_df.groupby('TradeSellNo').agg({'TradeMoney': sum,
                                                        'TradeIndex': max})  # 去除散户
    mid_big_group_sell = group_sell_df.query('TradeMoney > 50000')
    last_index = mid_big_group_sell['TradeIndex'].iloc[-1] if len(mid_big_group_sell) > 0 else 0
    last_buy = df[df['TradeIndex'] > last_index] if len(sell_df) != 0 else df

    if len(last_buy) == 0:
        ret = 0
    else:
        buy_deal_qty_max = last_buy.groupby('TradeBuyNo')['TradeQty'].sum().max()
        ret = buy_deal_qty_max / ff_shares / 1e4  # 最后最大买单的换手

    factor_dict = {factor_name: ret}

    return pd.Series(factor_dict)