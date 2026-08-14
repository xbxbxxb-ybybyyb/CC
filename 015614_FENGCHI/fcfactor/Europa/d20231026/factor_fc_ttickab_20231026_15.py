# coding: utf-8
# Author：fengchi863
# Date ：2023/5/10 21:13

import pandas as pd
import numpy as np
import datetime as dt
import decimal
def round_(x, n=0):
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))), rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

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

def factor_fc_ttickab_20231026_15(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # ---------------------------------------------突破前3分钟内30秒涨跌幅大于千5部分所占比例与前序区间差值---------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
    ZT_Time = df['MDTime'].max()
    pre_close = df['pre_close'].iloc[0]
    df = df[df['MDTime'] >= 93000000]

    df['itvl_pct'] = ((df['LastPx'] - df['LastPx'].shift(10)) / pre_close).apply(lambda x: round_(x, 4))
    if zcz: df['itvl_pct'] /= 2

    if len(df) <= 60:
        res = 0
    else:
        df_head = df.head(df.shape[0] - 60)
        res1 = df_head.query(f'itvl_pct >= 0.005').shape[0] / df_head.shape[0]
        df_tail = df.tail(60)
        res2 = df_tail.query(f'itvl_pct >= 0.005').shape[0] / df_tail.shape[0]
        res = res2 - res1

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    73.54 -0.1268
    =====>>>> 73.54166666666667 -0.1268030209164013 0.1910008424740276 0.21768427335294743 qyh_ttick_risespeed5_3m，xbc_20230831_9，xbc_20230928_6，xbc_20231012_6 0.8215，0.7865，0.677，0.6717 try
    """
    return pd.Series(factor_dict)