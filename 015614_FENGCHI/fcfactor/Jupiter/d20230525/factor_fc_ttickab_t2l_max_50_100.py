# coding: utf-8
# Author：fengchi863
# Date ：2023/5/24 9:09

import numpy as np
import pandas as pd


def factor_fc_ttickab_t2l_max_50_100(df, return_fillna_dic=False):
    # 最近50个tick，分两段区间内的最新价与twap的涨跌幅的最大值之和
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
    #df['lastPx_avgOfferPx_diff'] = df[['WeightedAvgOfferPx', 'LastPx']].apply(lambda x: x['WeightedAvgOfferPx'] - x['LastPx'] if x['WeightedAvgOfferPx'] != 0 else 0, axis=1).values.reshape(-1)
    df['lastPx_avgOfferPx_diff'] = (df['WeightedAvgOfferPx'] - df['LastPx'])
    df.loc[df['WeightedAvgOfferPx'] == 0, 'lastPx_avgOfferPx_diff'] = 0
    df['vwap'] = df["TotalValueTrade"] / df["TotalVolumeTrade"]
    df['twap'] = df['LastPx'].expanding().sum() / df['LastPx'].expanding().count()  # 只算了930之后的twap

    if len(df) > 100: # 在930之后涨停
        factor = (df['LastPx'] / df['twap'] - 1).iloc[-50:].max() + (df['LastPx'] / df['twap'] - 1).iloc[-100:-50].max()
    else:
        factor = 0.080885

    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)