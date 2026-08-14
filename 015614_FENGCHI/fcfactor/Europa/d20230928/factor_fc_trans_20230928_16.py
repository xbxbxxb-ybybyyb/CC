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


def factor_fc_trans_20230928_16(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0}

    # ------------------------------------------------近2分钟单订单号总量均值/近20分钟单订单号总量方差---------------------------------------------------------
    dt, Ticker = df.index[0]
    ff_shares = df['ff_shares'].iloc[0]
    zt_time = df['MDTime'].max()
    df = df[df['TradeMoney'] > 0]
    df = df[(df['TradeType'] == 0) & (df['TradePrice'] > 0)]
    df['buy_flag'] = (df['TradeBuyNo'] > df['TradeSellNo']).astype(float)
    df = df[df['MDTime'] >= 93000000]

    short_time = max(fun_get_time(zt_time, -120), 93000000)
    long_time = max(fun_get_time(zt_time, -1200), 93000000)
    short_df = df.query(f'MDTime >= {short_time}')
    long_df = df.query(f'MDTime >= {long_time}')

    if len(long_df) != 0:
        if long_df.groupby('TradeBuyNo').sum()['TradeQty'].std() == 0: ret = 0
        else: ret = short_df.groupby('TradeBuyNo').sum()['TradeQty'].mean() / long_df.groupby('TradeBuyNo').sum()['TradeQty'].std()
    else:
        ret = 1.0

    factor_dict = {factor_name: ret}
    """
    =====>>>> 63.37500000000001 0.09557414558850731 0.4810996778452109 0.3519290552774495 xbc_20230629_9，wj_TTick_pos_h2vwap_val 0.4724，0.4655
    """
    return pd.Series(factor_dict)