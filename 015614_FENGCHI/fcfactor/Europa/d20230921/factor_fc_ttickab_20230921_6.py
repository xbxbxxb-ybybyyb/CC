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


def factor_fc_ttickab_20230921_6(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0}

    # -----------------------------------------------突破前一段时间卖一盘口差异起末端均值涨跌----------------------------------------------------------
    dt, Ticker = df.index[0]
    pre_close = df['pre_close'].iloc[0]
    zt_time = int(df.iloc[-1]['MDTime'])
    df = df[df['MDTime'] >= 93000000]
    df['p2v'] = df['Sell1Price'] - df['WeightedAvgBidPx']
    df = df[df['MDTime'] >= max(fun_get_time(zt_time, -480), 93000000)]
    if len(df) > 0:
        res = (df['p2v'].tail(1).mean() - df['p2v'].head(1).mean()) / pre_close
    else:
        res = np.nan
    factor_dict = {factor_name: res}
    # -------------------------------------------------69.08 -0.12--------------------------------------------------------------
    # 69.08333333333334 -0.12025242034293893 0.04109521654653023 0.16541370991340473 xbc_20230914_7，xbc_20230914_13 0.6656，0.6388
    return pd.Series(factor_dict)