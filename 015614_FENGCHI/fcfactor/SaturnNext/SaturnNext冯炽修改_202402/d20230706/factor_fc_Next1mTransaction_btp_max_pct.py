# coding: utf-8
# Author：fengchi863
# Date ：2023/7/5 14:16

import datetime as dt
import sys
import pandas as pd
import numpy as np


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

def weight_mean(elements, weights=None):
    if not weights:
        weights = [i / len(elements) for i in range(1, len(elements) + 1)]
    if len(elements) == 0 or len(weights) == 0:
        return 0
    else:
        return np.mean([x*y for x, y in zip(elements, weights)])

import decimal
def round_(x, n=0):
    x = x + 1e-8
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))), rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

def factor_fc_Next1mTransaction_btp_max_pct(df, return_fillna_dic=False):
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    df = df[(df['TradePrice'] > 0) & (df['TradeMoney'] > 0)]  # 去除深圳撤单的逐笔成交数据
    df = df[df['MDTime'] >= 93000000]  # 选择连续竞价阶段的逐笔成交数据
    df['m'] = df['MDTime'] // 100000

    if len(df) == 0:
        return pd.Series({factor_name: 0})
    else:
        pre_close = df.iloc[0]['pre_close']

        df_low = df[df['TradeQty'] >= round_(df['TradeQty'].quantile(0.7), 6)]

        factor = ((df_low['TradePrice'] - df_low['TradePrice'].min()) / pre_close).max()

        factor_dict = {factor_name: factor}
    # print(factor_name, dt.strftime('%Y%m%d'), factor)
    #----------------------------930-931之间大单部分成交价格相对于最低价的最大值（负向，涨的越多，收益越低？） 16.67 -5.69-观察只在最大值附近单调性很强-------------------------------
    return pd.Series(factor_dict)

"""
df[(df['TradePrice'] > 0) & (df['TradeMoney'] > 0)]  # 去除深圳撤单的逐笔成交数据
df[df['MDTime'] >= 93000000]  # 选择连续竞价阶段的逐笔成交数据

MDTime
TradeIndex：成交编号
TradeBuyNo：买方委托序号 TradeBuyNo > TradeSellNo 主动买入 否则被动买入
TradeSellNo：卖方委托序号
TradeType：成交类别
TradeBSFlag：成交方向 1买 2卖
TradePrice：成交价格
TradeQty：成交数量
TradeMoney：成交金额，等于0是撤单的股票
pre_close：昨收价
ff_shares：流通股数
"""