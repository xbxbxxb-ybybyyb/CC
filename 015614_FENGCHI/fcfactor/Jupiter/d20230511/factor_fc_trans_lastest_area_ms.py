# coding: utf-8
# Author：fengchi863
# Date ：2023/5/10 21:13

import pandas as pd
import numpy as np
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


def factor_fc_trans_lastest_area_ms(df, return_fillna_dic=False):
    # inscore51.88 与vwap 0.73corr
    factor_name = 'fc_trans_lastest_area_ms'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    df = df[(df['TradePrice'] > 0)]  # 去除撤单
    df = df[df['MDTime'] >= 93000000]
    pre_close = df.iloc[-1]['pre_close']
    ul_price = np.floor(pre_close * 1.1 * 100 + 0.5) / 100 if not zcz else np.floor(pre_close * 1.2 * 100 + 0.5) / 100
    ul_time = df.iloc[-1]['MDTime']

    last_time = fun_get_time(int(ul_time), -3600)
    df = df.query(f'MDTime >= {last_time}')
    ms = (ul_price / df['TradePrice'] - 1).mean() * (ul_price / df['TradePrice'] - 1).std()

    if zcz:
        ms /= 2

    factor = ms
    factor_dict = {factor_name: factor}

    return pd.Series(factor_dict)