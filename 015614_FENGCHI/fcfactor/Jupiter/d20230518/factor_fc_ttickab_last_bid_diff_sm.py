# coding: utf-8
# Author：fengchi863
# Date ：2023/5/19 13:54

import numpy as np
import pandas as pd


def factor_fc_ttickab_last_bid_diff_sm(df, return_fillna_dic=False):
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
    df['WeightedAvgMidPx'] = (df['WeightedAvgBidPx'] + df['WeightedAvgOfferPx']) / 2
    df['lastPx_avgBidPx_diff'] = df['LastPx'] - df['WeightedAvgBidPx']
    df['lastPx_avgOfferPx_diff'] = df[['WeightedAvgOfferPx', 'LastPx']].apply(lambda x: x['WeightedAvgOfferPx'] - x['LastPx'] if x['WeightedAvgOfferPx'] != 0 else 0, axis=1).values.reshape(-1)

    if len(df) > 50: # 在930之后涨停
        if df['lastPx_avgBidPx_diff'].mean() != 0:
            factor = df['lastPx_avgBidPx_diff'].iloc[-50:].std() / df['lastPx_avgBidPx_diff'].iloc[-50:].mean()
        else:
            factor = 0
    else:
        factor = 0

    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)