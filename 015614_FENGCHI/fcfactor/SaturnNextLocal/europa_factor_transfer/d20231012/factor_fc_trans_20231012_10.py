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


def factor_fc_trans_20231012_10(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    # ------------------------------------------------近10秒同一卖方分组中非同价成交的比例/长区间非同价成交的比例---------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 1.0}

    dt, Ticker = df.index[0]
    ff_shares = df['ff_shares'].iloc[0]
    ZT_Time = df['MDTime'].iloc[-1]
    df = df[df['TradeMoney'] > 0]
    df['buy_flag'] = (df['TradeBuyNo'] > df['TradeSellNo']).astype(float)
    df = df[(df['TradeType'] == 0) & (df['TradePrice'] > 0)]

    short_time = 10
    long_time = 6000

    # ------------------------------------------------------------------------------------------------------------------
    start_time = max(fun_get_time(ZT_Time, -short_time), 93000000)
    short_df = df.query(f'MDTime >= {start_time}')
    short_group = short_df.groupby('TradeSellNo')
    short_group_df = pd.DataFrame()
    short_group_df['max'], short_group_df['min'] = short_group.max()['TradePrice'], short_group.min()['TradePrice']

    start_time = max(fun_get_time(ZT_Time, -long_time), 93000000)
    long_df = df.query(f'MDTime >= {start_time}')
    long_group = long_df.groupby('TradeSellNo')
    long_group_df = pd.DataFrame()
    long_group_df['max'], long_group_df['min'] = long_group.max()['TradePrice'], long_group.min()['TradePrice']

    long_pct = len(long_group_df[long_group_df['max'] != long_group_df['min']]) / (len(long_group_df) + 0.5)
    short_pct = len(short_group_df[short_group_df['max'] != short_group_df['min']]) / (len(short_group_df) + 0.5)

    ret = short_pct / (long_pct + 0.001)

    factor_dict = {factor_name: ret}
    # ---------------------------------------------------------------------------------------------------------------
    """
    53 -0.09
    =====>>>> 53.0 -0.09122585532786362 0.719308982767045 2.3630679645358397 t_down_ask_rate_sdl，xbc_20230921_4 0.4938，0.4864
    """
    return pd.Series(factor_dict)