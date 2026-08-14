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

def factor_fc_trans_20231026_5(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # ------------------------------------------------突破前长短区间的平均单笔净买入金额的差异------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    ZT_Time = df['MDTime'].max()
    pre_close = df['pre_close'].iloc[0]

    short_start_time = max(93000000, fun_get_time(ZT_Time, -20))
    long_start_time = max(93000000, fun_get_time(ZT_Time, -300))

    df['buy_flag'] = (df['TradeBuyNo'] > df['TradeSellNo']).replace({True: 1, False: -1})
    df['act_buy_amt'] = df['buy_flag'] * df['TradeMoney']
    res1 = df.query(f'MDTime > {short_start_time}')['act_buy_amt'].mean()
    res2 = df.query(f'MDTime > {long_start_time}')['act_buy_amt'].mean()

    factor_dict = {factor_name: res1 - res2}
    # ---------------------------------------------------------------------------------------------------------------
    """
    57.08 0.107
    =====>>>> 57.08333333333334 0.10700972979963567 6216.7203753711765 10444.676150202957 xbc_20230921_4，fc_trans_20231019_14 0.6659，0.6635
    """
    return pd.Series(factor_dict)