# coding: utf-8
# Author：fengchi863
# Date ：2023/5/19 16:07

import numpy as np
import pandas as pd


def factor_fc_ttickab_lp_op_diff_max_turn(df, return_fillna_dic=False):
    # 最近50个tick，最新价与卖均价的差值的最大值 / 昨收价
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    dt, Ticker = df.index[0]
    pre_close = df['pre_close'].iloc[0]
    ff_shares = df['ff_shares'].iloc[0]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    ul_price = np.floor(pre_close * 1.1 * 100 + 0.5 + 1e-8) / 100 if not zcz else np.floor(pre_close * 1.2 * 100 + 0.5 + 1e-8) / 100
    dt_price = np.floor(pre_close * 0.9 * 100 + 0.5 + 1e-8) / 100 if not zcz else np.floor(pre_close * 0.8 * 100 + 0.5 + 1e-8) / 100
    df = df[df['MDTime'] >= 93000000]

    df['diffPx'] = df['WeightedAvgBidPx'] - df['WeightedAvgOfferPx']
    df['WeightedAvgMidPx'] = (df['WeightedAvgBidPx'] + df['WeightedAvgOfferPx']) / 2
    df['lastPx_avgBidPx_diff'] = df['LastPx'] - df['WeightedAvgBidPx']
    #df['lastPx_avgOfferPx_diff'] = df[['WeightedAvgOfferPx', 'LastPx']].apply(lambda x: x['WeightedAvgOfferPx'] - x['LastPx'] if x['WeightedAvgOfferPx'] != 0 else 0, axis=1).values.reshape(-1)
    df['lastPx_avgOfferPx_diff'] = (df['WeightedAvgOfferPx'] - df['LastPx'])
    df.loc[df['WeightedAvgOfferPx'] == 0, 'lastPx_avgOfferPx_diff'] = 0

    if len(df) > 50: # 在930之后涨停
        factor = df['lastPx_avgOfferPx_diff'].iloc[-50:].max() / pre_close
    else:
        factor = 0.025

    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)