# coding: utf-8
# Author：fengchi863
# Date ：2023/6/14 10:29

import numpy as np
import pandas as pd
import sys

def weight_mean(elements, weights=None):
    if not weights:
        weights = [i / len(elements) for i in range(1, len(elements) + 1)]
    if len(elements) == 0 or len(weights) == 0:
        return 0
    else:
        return np.mean([x*y for x, y in zip(elements, weights)])

def factor_fc_order_9pct_ul_ratio(df, return_fillna_dic=False):
    # 逐笔委托中，90%分位数相对于涨停价的涨幅，表征委托价格走势  得分53.75 与自己高相关，得分比他高一点
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    pre_close = df['pre_close'].iloc[0]
    dt, Ticker = df.index[0]
    ff_shares = df['ff_shares'].iloc[0]
    df = df[df['OrderType'].isin([1, 2]) & df['OrderBSFlag'].isin([1])]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    ul_price = np.floor(pre_close * 1.1 * 100 + 0.5 + 1e-8) / 100 if not zcz else np.floor(pre_close * 1.2 * 100 + 0.5 + 1e-8) / 100
    dt_price = np.floor(pre_close * 0.9 * 100 + 0.5 + 1e-8) / 100 if not zcz else np.floor(pre_close * 0.8 * 100 + 0.5 + 1e-8) / 100
    df.loc[(df['OrderType'] == 1) & (df['OrderBSFlag'] == 1), 'OrderPrice'] = ul_price
    df.loc[(df['OrderType'] == 1) & (df['OrderBSFlag'] == 2), 'OrderPrice'] = dt_price
    df = df.query(f'{dt_price} <= OrderPrice <= {ul_price}')
    df['m'] = df['MDTime'] // 100000
    df['TradeMoney'] = df['OrderPrice'] * df['OrderQty']

    min_price = df.groupby('m')['OrderPrice'].quantile(0.9)
    if len(min_price) >= 1:
        factor = (min_price / ul_price - 1).mean()
    else:
        factor = 0

    if zcz: factor /= 2

    #print(factor_name, dt.strftime('%Y%m%d'), factor)
    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

"""
MDTime: 时间
OrderIndex: 委托编号：可以在Trans中查询到这个号
OrderType: 委托类别：1市价2限价
OrderPrice: 委托价格，对于4、5、6、7会有0的情况，只筛选1和2的，对于市价单设置为涨停跌停价
OrderQty: 委托数量
OrderBSFlag: 委托方向，1买2卖
"""