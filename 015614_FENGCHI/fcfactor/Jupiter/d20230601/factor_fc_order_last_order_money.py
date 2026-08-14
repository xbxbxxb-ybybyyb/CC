# coding: utf-8
# Author：fengchi863
# Date ：2023/5/31 15:36

import numpy as np
import pandas as pd
import sys


def weight_mean(elements, weights):
    if len(elements) == 0 or len(weights) == 0:
        return 0
    else:
        return np.sum([x * y for x, y in zip(elements, weights)]) / np.sum(weights)


def factor_fc_order_last_order_money(df, return_fillna_dic=False):
    # 最后一段时间买单下单金额的均值
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    df = df[df['OrderType'].isin([1, 2]) & df['OrderBSFlag'].isin([1])]
    df['TradeMoney'] = df['OrderPrice'] * df['OrderQty']

    if len(df) > 100:
        df = df.tail(100)

    if len(df) != 0:
        factor = weight_mean(df['TradeMoney'].tolist(), [i / len(df) for i in range(1, len(df) + 1)])
    else:
        factor = 0

    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)