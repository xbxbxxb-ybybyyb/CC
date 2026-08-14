# coding: utf-8
# Author：fengchi863
# Date ：2023/6/13 10:39

import datetime as dt
import sys
import pandas as pd
from scipy.stats import pearsonr


def fun_get_time(time1, sec_delta):
    # 计算给定时间戳time1在sec_delta秒后的时间戳
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

def factor_fc_trans_10s_bs_qty_r(df, param_tuple=(), return_fillna_dic=False):
    # 逐笔成交10秒买单量与卖单量的相关性 28.92 赌一把，估计过不了
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0}
    df = df[(df['TradePrice'] > 0) & (df['TradeMoney'] > 0)]  # 去除深圳撤单的逐笔成交数据
    df = df[df['MDTime'] >= 93000000]  # 选择连续竞价阶段的逐笔成交数据
    df['m'] = df['MDTime'] // 10000
    # ul_time = df.iloc[-1]['MDTime']

    min_buy_qty = df.query('TradeBSFlag == 1').groupby('m')['TradeQty'].sum()
    min_sell_qty = df.query('TradeBSFlag == 2').groupby('m')['TradeQty'].sum()

    if len(min_buy_qty) == 0:
        factor = 1.0
    elif len(min_sell_qty) == 0:
        factor = 1.0
    else:
        # index = list(set(min_sell_qty.index).intersection(set(min_buy_qty.index)))
        index = sorted(list(set(min_sell_qty.index).union(set(min_buy_qty.index))))
        min_buy_qty = min_buy_qty.reindex(index=index).fillna(0)
        min_sell_qty = min_sell_qty.reindex(index=index).fillna(0)
        factor = pearsonr(min_buy_qty.loc[index], min_sell_qty.loc[index])[0]

    factor_dict = {factor_name: factor}

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