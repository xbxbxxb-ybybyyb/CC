# coding: utf-8
# Author：fengchi863
# Date ：2023/3/21 17:01

# -*- coding: utf-8 -*-
import pandas as pd
import datetime as dt

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


def factor_test_trade_factor(df, param_tuple, return_fillna_dic=False):
    factor_name = 'test_trade_factor'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')

    df = df[(df['TradePrice'] > 0)]  # 去除撤单
    df = df[df['MDTime'] >= 93000000]
    pre_close = df.iloc[-1]['pre_close']
    ul_time = df.iloc[-1]['MDTime']

    #----------------------------------
    # 触发前30/60/300秒
    # target_time = fun_get_time(int(ul_time), -60)
    # df = df.query(f'MDTime >= {target_time}')
    # # 触发前100/500/1000单
    if len(df) > 100:
        df = df.iloc[-100:]
    else:
        df = df
    # 首次超过0.09, 0.095, 0.098
    # df['idx'] = range(0, len(df))
    # pct9_price = pre_close * (1 + 0.09) if not zcz else pre_close * (1 + 0.09 * 2)
    # first_idx = df.query(f'TradePrice >= {pct9_price}').iloc[0]['idx']
    # df = df.query(f'idx >= {first_idx}')

    #----------------------------------
    deal_df = df.query(f'TradeMoney > 200000')
    if deal_df.shape[0] != 0:
        ret = deal_df['TradeMoney'].sum() / df['TradeMoney'].sum()
    else:
        ret = 0

    factor = ret
    factor_dict = {factor_name: factor}

    return pd.Series(factor_dict)
