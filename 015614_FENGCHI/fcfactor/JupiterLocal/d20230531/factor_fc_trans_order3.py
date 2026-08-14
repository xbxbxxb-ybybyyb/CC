# coding: utf-8
# Author：fengchi863
# Date ：2023/6/8 16:05

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

def factor_fc_trans_order3(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # -------------------------------------------------------------------------------------------------------------------
    dt, Ticker = df.index[0]
    pre_close = df['pre_close'].iloc[0]
    # ff_shares = df['ff_shares'].iloc[0]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    ul_price = np.floor(pre_close * 1.1 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 1.2 * 100 + 0.5) / 100
    dt_price = np.floor(pre_close * 0.9 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 0.8 * 100 + 0.5) / 100
    zt_time = df['MDTime'].max()

    trans_df = df.query('type == 0')[['MDTime', 'TradeBuyNo', 'TradeSellNo', 'TradePrice', 'TradeQty', 'TradeMoney']].copy()
    trans_df = trans_df.query('MDTime > 93000000')
    trans_df['m'] = trans_df['MDTime'] // 100000
    trans_df = trans_df[trans_df['TradeMoney'] > 0]
    trans_df['buy_flag'] = (trans_df['TradeBuyNo'] > trans_df['TradeSellNo']) * 1.0

    order_df = df.query('type == 1')[['MDTime', 'OrderIndex', 'OrderType', 'OrderPrice', 'OrderQty', 'OrderBSFlag']].copy()
    order_df['m'] = order_df['MDTime'] // 100000
    order_df = order_df[order_df['OrderBSFlag'].isin([1, 2])]
    order_df.loc[(order_df['OrderType'] == 1) & (order_df['OrderBSFlag'] == 1), 'OrderPrice'] = ul_price
    order_df.loc[(order_df['OrderType'] == 1) & (order_df['OrderBSFlag'] == 2), 'OrderPrice'] = dt_price
    order_df = order_df.query(f'{dt_price} <= OrderPrice <= {ul_price}')
    order_df['OrderMoney'] = order_df['OrderPrice'] * order_df['OrderQty']

    target_time = max(fun_get_time(zt_time, -60), 93000000)
    tmp_trans_df = trans_df.query(f'MDTime >= {target_time}')
    tmp_order_df = order_df.query(f'MDTime >= {target_time}')

    tmp_trans_df = tmp_trans_df.query('buy_flag == 0')
    tmp_order_df = tmp_order_df.query('OrderBSFlag == 1')

    if len(tmp_order_df) > 0 and len(tmp_trans_df) > 0 and tmp_order_df['OrderMoney'].sum() != 0:
        factor = tmp_trans_df['TradeMoney'].sum() / tmp_order_df['OrderMoney'].sum()
    else:
        factor = 0

    print(factor_name, dt.strftime('%Y%m%d'), factor)
    factor_dict = {factor_name: factor}
    # -------------------------------------------35.71 -7.84 和王敬一个因子高相关wj_T1min_MoneyRatio 0.8705------------------------------------------------------------
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