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


def factor_fc_ttickab_20230921_22(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0.0085}

    # -----------------------------------------------全天分段vwap cv----------------------------------------------------------
    dt, Ticker = df.index[0]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    pre_close = df['pre_close'].iloc[0]
    zt_time = int(df.iloc[-1]['MDTime'])
    df = df[df['MDTime'] >= 93000000]

    df['ValueTrade'] = df['TotalValueTrade'] - df['TotalValueTrade'].shift(1).fillna(0)
    df['VolumeTrade'] = df['TotalVolumeTrade'] - df['TotalVolumeTrade'].shift(1).fillna(0)
    df = df[df['MDTime'] >= max(fun_get_time(zt_time, -24000), 93000000)]
    df = df.tail(int(len(df) / 5))
    df['vwap'] = df['ValueTrade'].cumsum() / df['VolumeTrade'].cumsum()
    mean = (df['vwap'] / df['LastPx']).mean()
    std = (df['vwap'] / df['LastPx']).std()
    factor = std / (mean + 0.000001)

    factor_dict = {factor_name: factor}
    # =====>>>> 73.66666666666667 -0.1371387216832042 0.0063311246258504275 0.003074594032188816 qyh_ttick_v2p_h2_cv，skk_TTickab_LPR_roll2vwap_std_a，qyh_ttick_sp_cv_h2_amtb 0.7037，0.6761，0.6517
    return pd.Series(factor_dict)