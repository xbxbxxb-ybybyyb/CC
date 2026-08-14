# coding: utf-8
# Author：fengchi863
# Date ：2023/5/31 11:04

import numpy as np
import sys
import pandas as pd


def factor_fc_order_last5order_qrr(df, param_tuple=(), return_fillna_dic=False):
    # 最后一段时间内最大5笔订单相对全天量比
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    pre_close = df['pre_close'].iloc[0]
    dt, Ticker = df.index[0]
    ff_shares = df['ff_shares'].iloc[0]
    df = df[df['OrderType'].isin([1, 2]) & df['OrderBSFlag'].isin([1])]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    df['TradeMoney'] = df['OrderPrice'] * df['OrderQty']

    if len(df) > 50:
        df_orderqty_sort = df.iloc[-50:]['OrderQty'].sort_values()
        factor = df_orderqty_sort[-5:].mean() / df['OrderQty'].mean()
    else:
        factor = 0

    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
