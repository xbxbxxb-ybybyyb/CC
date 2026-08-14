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


def factor_fc_ttickab_20230914_10(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0}

    # -----------------------------------------------当天成交尾部均价与买入加权均价的差值CV----------------------------------------------------------
    dt, Ticker = df.index[0]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    pre_close = df['pre_close'].max()
    df = df[df['MDTime'] >= 93000000]

    df['WindowValue'] = df['TotalValueTrade'] - df['TotalValueTrade'].shift(1).fillna(0)
    df['WindowVolume'] = df['TotalVolumeTrade'] - df['TotalVolumeTrade'].shift(1).fillna(0)
    trade_small = df['WindowValue'].quantile(0.4)
    df_small = df[df['WindowValue'] <= trade_small]
    df_small['factor'] = (df_small['WindowValue'] / df_small['WindowVolume'] - df_small['WeightedAvgBidPx']) / pre_close
    value = df_small['factor'].std() * df_small['factor'].mean()

    if np.isnan(value) or np.isinf(value):
        value = 0

    factor_dict = {factor_name: value}
    # -------------------------------------------------34.66 0.0756--------------------------------------------------------------
    return pd.Series(factor_dict)