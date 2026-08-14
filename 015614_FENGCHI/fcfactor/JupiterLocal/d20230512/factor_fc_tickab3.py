# coding: utf-8
# Author：fengchi863
# Date ：2023/5/12 16:04

import numpy as np
import pandas as pd


def factor_fc_tickab3(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    dt, Ticker = df.index[0]
    pre_close = df['pre_close'].iloc[0]
    ff_shares = df['ff_shares'].iloc[0]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    ul_price = np.floor(pre_close * 1.1 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 1.2 * 100 + 0.5) / 100
    dt_price = np.floor(pre_close * 0.9 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 0.8 * 100 + 0.5) / 100
    df = df[df['MDTime'] >= 93000000]

    df['diffPx'] = df['WeightedAvgBidPx'] - df['WeightedAvgOfferPx']
    # df['WeightedAvgMidPx'] = df[['WeightedAvgBidPx', 'WeightedAvgOfferPx']].apply(lambda x: (x['WeightedAvgBidPx'] + x['WeightedAvgOfferPx']) / 2 if x['WeightedAvgOfferPx'] != 0 else x['WeightedAvgBidPx'], axis=1).values.reshape(-1)
    # df['lastPx_avgBidPx_diff'] = df['LastPx'] - df['WeightedAvgBidPx']
    # df['lastPx_avgOfferPx_diff'] = df[['WeightedAvgOfferPx', 'LastPx']].apply(lambda x: x['WeightedAvgOfferPx'] - x['LastPx'] if x['WeightedAvgOfferPx'] != 0 else 0, axis=1).values.reshape(-1)
    df['vwap'] = df["TotalValueTrade"] / df["TotalVolumeTrade"]
    df['twap'] = df['LastPx'].expanding().sum() / df['LastPx'].expanding().count()  # 只算了930之后的twap

    # 积极买入 保守买入
    # comp_df = df.shift(1)
    # df['pos_buy'] = df['LastPx'] >= comp_df['Sell1Price']  # 下一个tick最新价大于等于上一个tick卖1价
    # df['neg_buy'] = df['LastPx'] <= comp_df['Buy1Price']  # 下一个tick最新价小于等于上一个tick买1价
    # df['TickVolumeTrade'] = df['TotalVolumeTrade'] - comp_df['TotalVolumeTrade']  # 每个tick成交的量
    df['slope'] = (df['Sell1Price'] - df['Buy1Price']) / (df['Sell1OrderQty'] + df['Buy1OrderQty']) * 2 # 斜率 价差/深度

    if len(df) > 50:
        factor = df['slope'].iloc[-50:].mean()
    else:
        factor = 0

    """积极买入和保守买入的不太有用
    if df.query('neg_buy == 1')['TickVolumeTrade'].sum():
        factor = df.query('pos_buy == 1')['TickVolumeTrade'].sum() / df.query('neg_buy == 1')['TickVolumeTrade'].sum()
    else:
        factor = 0
    """
    """已通过测试
    if len(df) > 100: # 在930之后涨停
        factor = (df['LastPx'] / df['twap'] - 1).iloc[-50:].max() + (df['LastPx'] / df['twap'] - 1).iloc[-100:-50].max()
    else:
        # factor = 0.065
        factor = 0.080885
    """

    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)