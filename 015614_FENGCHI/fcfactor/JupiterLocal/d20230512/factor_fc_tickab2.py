# coding: utf-8
# Author：fengchi863
# Date ：2023/5/12 16:04

import numpy as np
import pandas as pd


def factor_fc_tickab2(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    dt, Ticker = df.index[0]
    pre_close = df['pre_close'].iloc[0]
    ff_shares = df['ff_shares'].iloc[0]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    # ul_price = np.floor(pre_close * 1.1 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 1.2 * 100 + 0.5) / 100
    # dt_price = np.floor(pre_close * 0.9 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 0.8 * 100 + 0.5) / 100
    df = df[df['MDTime'] > 93000000]

    # df['diffPx'] = df['WeightedAvgBidPx'] - df['WeightedAvgOfferPx']
    # df['WeightedAvgMidPx'] = df[['WeightedAvgBidPx', 'WeightedAvgOfferPx']].apply(lambda x: (x['WeightedAvgBidPx'] + x['WeightedAvgOfferPx']) / 2 if x['WeightedAvgOfferPx'] != 0 else x['WeightedAvgBidPx'], axis=1).values.reshape(-1)
    # df['lastPx_avgBidPx_diff'] = df['LastPx'] - df['WeightedAvgBidPx']
    # df['lastPx_avgOfferPx_diff'] = df[['WeightedAvgOfferPx', 'LastPx']].apply(lambda x: x['WeightedAvgOfferPx'] - x['LastPx'] if x['WeightedAvgOfferPx'] != 0 else 0, axis=1).values.reshape(-1)
    # df['vwap'] = df["TotalValueTrade"] / df["TotalVolumeTrade"]
    # df['twap'] = df['LastPx'].expanding().sum() / df['LastPx'].expanding().count()   # 只算了930之后的twap
    BuyNOrderQtyList = [f'Buy{x}OrderQty' for x in range(1, 11)]
    SellNOrderQtyList = [f'Sell{x}OrderQty' for x in range(1, 11)]
    df['BuyOrderQtySum'] = df[BuyNOrderQtyList].sum(axis=1)
    df['SellOrderQtySum'] = df[SellNOrderQtyList].sum(axis=1)
    if df['SellOrderQtySum'].iloc[-5:].sum() != 0:
        factor = df['BuyOrderQtySum'].iloc[-5:].sum() / df['SellOrderQtySum'].iloc[-5:].sum()
    else:
        factor = 0
    """
    if len(df) > 10:  # 在930之后涨停
        # 最后50tick 保守买入量占比
        # factor = df.iloc[-50:].query('neg_buy == 1')['TickVolumeTrade'].sum() / df.iloc[-50:]['TickVolumeTrade'].sum()  # 没用 得分0.42
        # factor = df.iloc[-50:].query('pos_buy == 1')['TickVolumeTrade'].sum() / ff_shares  # 没用 得分0.42
    else:
        factor = 0
    """

    """
    if len(df) > 50 and (df['LastPx'] / df['twap'] - 1).iloc[-50:].mean() != 0: # 在930之后涨停
        # factor = df['lastPx_avgBidPx_diff'].iloc[-50:].std() / df['lastPx_avgBidPx_diff'].iloc[-50:].mean()
        # factor = df['lastPx_avgBidPx_diff'].iloc[-50:].max() / pre_close    # 18.92 5.73
        # factor = df['WeightedAvgMidPx'].iloc[-50:].max() / pre_close
        factor = (df['LastPx'] / df['twap'] - 1).iloc[-50:].std() / (df['LastPx'] / df['twap'] - 1).iloc[-50:].mean()
    else:
        factor = 0.0
    """

    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)