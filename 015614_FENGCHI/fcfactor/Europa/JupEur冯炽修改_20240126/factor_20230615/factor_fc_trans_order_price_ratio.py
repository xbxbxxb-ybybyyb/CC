# coding: utf-8
# Author：fengchi863
# Date ：2023/6/14 9:34

import datetime as dt

import numpy as np
import pandas as pd


def fun_get_time(time1, sec_delta):
    tmp_time = dt.datetime.strptime(str(time1)[:-3], '%H%M%S')
    tmp_time2 = tmp_time + dt.timedelta(seconds=sec_delta)
    tmp_time2_str = tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
    if (int(tmp_time2_str) > 113000000) & (time1 <= 113000000):
        adj_tmp_time2 = tmp_time2 + dt.timedelta(seconds=1.5 * 3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str) < 130000000) & (time1 >= 130000000):
        adj_tmp_time2 = tmp_time2 - dt.timedelta(seconds=1.5 * 3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str) < 93000000) & (time1 >= 93000000):
        adj_tmp_time2_str = '92500000'
        return int(adj_tmp_time2_str)
    elif time1 < 93000000:
        adj_tmp_time2 = tmp_time2 + dt.timedelta(seconds=4 * 60)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
        return int(adj_tmp_time2_str)
    else:
        return int(tmp_time2_str)

def weight_mean(elements, weights):
    if len(elements) == 0 or len(weights) == 0:
        return 0
    else:
        return np.mean([x*y for x, y in zip(elements, weights)])

def factor_fc_trans_order_price_ratio(df, return_fillna_dic=False):
    # # 逐笔成交中，分钟最高价相对于分钟委托最高价涨跌幅（得分低必不过，结果呈非线性，反而中间一部分区域具有单调性）
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    dt, Ticker = df.index[0]
    pre_close = df['pre_close'].iloc[0]
    ff_shares = df['ff_shares'].iloc[0]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    ul_price = np.floor(pre_close * 100 * 1.1 + 0.5 + 1e-8) / 100 if not zcz else np.floor(pre_close * 100 * 1.2 + 0.5 + 1e-8) / 100
    dt_price = np.floor(pre_close * 100 * 0.9 + 0.5 + 1e-8) / 100 if not zcz else np.floor(pre_close * 100 * 0.8 + 0.5 + 1e-8) / 100
    zt_time = df['MDTime'].max()

    trans_df = df.query('type == 0')[['MDTime', 'TradeBuyNo', 'TradeSellNo', 'TradePrice', 'TradeQty', 'TradeMoney']].copy()
    trans_df = trans_df.query('MDTime >= 93000000 & TradePrice > 0')
    trans_df['m'] = trans_df['MDTime'] // 100000
    trans_df = trans_df[trans_df['TradeMoney'] > 0]
    trans_df['buy_flag'] = (trans_df['TradeBuyNo'] > trans_df['TradeSellNo']) * 1.0

    order_df = df.query('type == 1')[['MDTime', 'OrderIndex', 'OrderType', 'OrderPrice', 'OrderQty', 'OrderBSFlag']].copy()
    order_df = order_df.query('MDTime >= 93000000')
    order_df['m'] = order_df['MDTime'] // 100000
    order_df = order_df[order_df['OrderBSFlag'].isin([1, 2])]
    order_df = order_df.query(f'{dt_price} <= OrderPrice <= {ul_price}')
    order_df['OrderMoney'] = order_df['OrderPrice'] * order_df['OrderQty']

    # target_time = fun_get_time(zt_time, -120)
    if len(order_df) > 0 and len(trans_df) > 0:
        order_price_group_min = order_df.groupby('m')['OrderPrice'].quantile(0.9)  # order数据中OrderPrice最大值不可，因为大部分时间都有挂涨停买入的，所以取分位数
        trans_price_group_min = trans_df.groupby('m')['TradePrice'].max()
        factor = (trans_price_group_min / order_price_group_min - 1).dropna().mean()

        if ~np.isfinite(factor):
            factor = 0
    else:
        factor = 0

    #print(factor_name, dt.strftime('%Y%m%d'), factor)
    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

"""
MDTime: 时间 如101215000
TradeIndex：成交编号，与OrderIndex可匹配
TradeBuyNo：买方委托序号 TradeBuyNo > TradeSellNo 主动买入 否则被动买入
TradeSellNo：卖方委托序号
# 以上委托序号与OrderIndex相同
TradeType：成交类别
TradeBSFlag：成交方向 1买 2卖
TradePrice：成交价格
TradeQty：成交数量
TradeMoney：成交金额，等于0是撤单的股票
pre_close：昨收价
ff_shares：流通股数

MDTime: 时间
OrderIndex: 委托编号：可以在Trans中查询到这个号
OrderType: 委托类别：1市价2限价
OrderPrice: 委托价格，对于4、5、6、7会有0的情况，只筛选1和2的，对于市价单设置为涨停跌停价
OrderQty: 委托数量
OrderBSFlag: 委托方向，1买2卖
"""