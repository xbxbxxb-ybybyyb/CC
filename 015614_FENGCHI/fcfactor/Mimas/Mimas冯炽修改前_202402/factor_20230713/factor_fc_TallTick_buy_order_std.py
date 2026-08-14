# coding: utf-8
# Author：fengchi863
# Date ：2023/7/13 20:05

import numpy as np
import pandas as pd


def factor_fc_TallTick_buy_order_std(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    dt, Ticker = df.index[0]
    df = df[df['MDTime'] >= 93000000]

    if df.shape[0] >= 0:
        factor = (df['Buy1OrderQty'] + df['Buy2OrderQty']).std()
    else:
        factor = 0

    # print(factor_name, dt.strftime('%Y%m%d'), factor)
    factor_dict = {factor_name: factor}
    # -------------------------------------------------买入次日Tick盘口买1与卖2 量的标准差 21.92 -6.73 -------------------------------------------------------
    return pd.Series(factor_dict)