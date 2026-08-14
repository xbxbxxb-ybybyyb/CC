# coding: utf-8
# Author：fengchi863
# Date ：2023/7/13 13:15

import datetime as dt
import sys
import pandas as pd
from scipy.stats import pearsonr
import numpy as np

def factor_fc_TallTrans_p2ul_pstd(df, return_fillna_dic=False):
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    # ul_time = df.iloc[-1]['MDTime']
    pre_close = df.iloc[-1]['pre_close']
    df = df[(df['TradePrice'] > 0)]  # 去除撤单
    df = df[df['MDTime'] >= 93000000]
    ul_price = np.floor(pre_close * 1.1 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 1.2 * 100 + 0.5) / 100

    factor = (ul_price / df['TradePrice'] - 1).std()

    # print(factor_name, dt.strftime('%Y%m%d'), factor)
    factor_dict = {factor_name: factor}
    # ------------------------成交价与ul_price的pct标准差--20.67 -5.63 ------------------------------
    return pd.Series(factor_dict)

"""
MDTime
TradeIndex
TradeBuyNo
TradeSellNo
TradeType：
TradeBSFlag：1买2卖
TradePrice
TradeQty
TradeMoney
pre_close
ff_shares
"""