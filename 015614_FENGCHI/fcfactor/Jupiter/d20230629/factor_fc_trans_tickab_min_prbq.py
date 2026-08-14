# coding: utf-8
# Author：fengchi863
# Date ：2023/6/27 8:39

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


def factor_fc_trans_tickab_min_prbq(df, return_fillna_dic=False):
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
    zt_time = df['MDTime'].max()

    trans_df = df.query('type == 0')[['MDTime', 'TradeIndex', 'TradeBuyNo', 'TradeSellNo', 'TradePrice', 'TradeQty', 'TradeMoney']].copy()
    trans_df = trans_df.query('MDTime > 93000000')
    trans_df['m'] = trans_df['MDTime'] // 10000
    trans_df = trans_df[trans_df['TradeMoney'] > 0]
    trans_df['buy_flag'] = (trans_df['TradeBuyNo'] > trans_df['TradeSellNo']) * 1.0

    tick_df = df.query('type == 1')[['MDTime', 'LastPx', 'TotalOfferQty', 'TotalBidQty', 'WeightedAvgBidPx', 'WeightedAvgOfferPx', 'NumTrades']].copy()
    tick_df['m'] = tick_df['MDTime'] // 10000
    tick_df['diffPx'] = tick_df['WeightedAvgBidPx'] - tick_df['WeightedAvgOfferPx']
    tick_df['tickNumTrades'] = tick_df['NumTrades'].diff().fillna(0)

    target_time = max(fun_get_time(zt_time, -120), 93000000)    # 5分钟

    tmp_trans_df = trans_df.query(f'MDTime >= {target_time}')
    tmp_tick_df = tick_df.query(f'MDTime >= {target_time}')

    min_trans_qty = tmp_trans_df.query('buy_flag == 1').groupby('m')['TradeQty'].sum(min_count=1)
    min_tick_nums = tmp_tick_df.groupby('m')['tickNumTrades'].sum(min_count=1)

    if len(min_trans_qty) > 0 and len(min_tick_nums) > 0:
        factor_s = min_trans_qty / min_tick_nums
        factor_s.loc[factor_s[factor_s==np.inf].index] = 0
        target = factor_s.iloc[-2:].sum()
        factor = target / ff_shares
    else:
        factor = 0

    print(factor_name, dt.strftime('%Y%m%d'), factor)
    factor_dict = {factor_name: factor}
    # ------------------------------成交数量除以成交笔数，最近一小段时间平均每笔交易的买单量对应换手--65.58 9.71 没有高相关----------------------------------------
    return pd.Series(factor_dict)

"""
MDTime: 时间 如101215000
TradeBSFlag：不用这个
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
WeightedAvgOfferPx：本tick平均买入价
WeightedAvgBidPx：本tick平均卖出价
LastPx：最新价
TotalOfferQty：卖出总量
TotalBidQty：买入总量
NumTrades：从开盘到现在成交笔数，切记是总成交，所以要diff()

"""