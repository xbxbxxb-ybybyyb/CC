# -*- coding: utf-8 -*-
import pandas as pd
import os
import numpy as np
from scipy.stats import skew, kurtosis
import math
import sys
FACTOR_NAME = 'qyh_20240201_test'
FACTOR_TYPE = 'TTickab_MetisAll'
EPS=1e-9
def preprocess_TTick_zwh(data_df):
    dt, ticker = data_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = data_df['pre_close'].values[0]
    price_names = ['LastPx', 'HighPx', 'LowPx', 'WeightedAvgBidPx', 'WeightedAvgOfferPx',
                   'Buy1Price', 'Buy2Price', 'Buy3Price', 'Buy4Price', 'Buy5Price', 'Buy6Price', 'Buy7Price',
                   'Buy8Price', 'Buy9Price', 'Buy10Price', 'Sell1Price', 'Sell2Price', 'Sell3Price', 'Sell4Price',
                   'Sell5Price', 'Sell6Price', 'Sell7Price', 'Sell8Price', 'Sell9Price', 'Sell10Price']
    if zcz:
        data_df[price_names] = ((data_df[price_names] / pre_close - 1) / 2 + 1) * pre_close
    return data_df
def factor_qyh_20240201_test(tick_df, return_fillna_dic=False):
    factor_name = FACTOR_NAME
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    pre_close = tick_df['pre_close'].values[0]
    tick_df = preprocess_TTick_zwh(tick_df)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    if tick_df.shape[0] > 0:
        xx = tick_df['pre_close']
        yy = tick_df['WeightedAvgBidPx']-tick_df['LastPx']
        def sta(data):
            out  =data.median()/(EPS+data.min()) + data.min()
            return out
        result = sta(xx/(EPS +yy))
    else:
        result = 0.0
    # print(result)
    factor_dict = {factor_name: result/1e4}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)