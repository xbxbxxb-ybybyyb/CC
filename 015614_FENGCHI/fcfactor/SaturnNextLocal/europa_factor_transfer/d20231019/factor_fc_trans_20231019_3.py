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

def cal_time_delta(start, end):
    start_str = str(int(start))
    end_str = str(int(end))
    time_delta = (int(end_str[:~6]) - int(start_str[:~6])) * 3600000 + \
                 (int(end_str[~6:~4]) - int(start_str[~6:~4])) * 60000 + \
                 (int(end_str[~4:~2]) - int(start_str[~4:~2])) * 1000 + \
                 (int(end_str[~2:]) - int(start_str[~2:]))
    if (start < 120000000) & (end > 120000000):
        time_delta = time_delta - 5400000
    return time_delta

def cal_time_dis(s1, s2):
    s1_value = s1.values
    s2_value = s2.values
    delta_time_list = list()
    for j in range(len(s1_value)):
        delta_time_list.append(cal_time_delta(s1_value[j], s2_value[j]))
    delta_time = pd.Series(delta_time_list, index=s2.index)
    return delta_time

def fun_shift_time(start_time, shift_time):
    start_str = str(start_time)
    end_int = int(start_str[:~6]) * 3600000 + \
              int(start_str[~6:~4]) * 60000 + \
              int(start_str[~4:~2]) * 1000 + \
              int(start_str[~2:]) + shift_time
    end_time = int((end_int - np.floor(end_int / 1000) * 1000) + \
                   (np.floor(end_int / 1000) - np.floor(end_int / 60000) * 60) * 1000 + \
                   (np.floor(end_int / 60000) - np.floor(end_int / 3600000) * 60) * 100000 + \
                   (np.floor(end_int / 3600000)) * 10000000)
    if (start_time < 113000000) & (end_time > 113000000) & (end_time < 130000000):
        end_time = fun_shift_time(end_time, 5400000)
    if (start_time > 130000000) & (end_time < 130000000) & (end_time > 113000000):
        end_time = fun_shift_time(end_time, -5400000)
    return max(93000000, end_time)

def factor_fc_trans_20231019_3(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # ----------------------------------------------------突破前短区间与长区间内按买单号标准差比值的差值-----------------------------------------------------
    if return_fillna_dic:
        return {factor_name: -1.0}

    ZT_Time = df['MDTime'].iloc[-1]
    pre_close = df['pre_close'].max()
    df = df[(df['TradeType'] == 0) & (df['TradePrice'] > 0) & (df['TradeQty'] > 0) & (df['MDTime'] > 93000000)]

    df_copy = df.set_index('TradeBuyNo').drop_duplicates('MDTime', keep='last')

    dis2opn = cal_time_delta(93000000, ZT_Time)
    short_time = fun_shift_time(ZT_Time, -min(20000, int(dis2opn / 20)))
    long_time = fun_shift_time(ZT_Time, -min(90000, int(dis2opn / 2)))
    short_std = np.std(df_copy[df_copy['MDTime'] >= short_time]['TradePrice'] / pre_close - 1) / (np.std(df_copy['TradePrice'] / pre_close - 1) + 0.001)
    long_std = np.std(df_copy[df_copy['MDTime'] >= long_time]['TradePrice'] / pre_close - 1) / (np.std(df_copy['TradePrice'] / pre_close - 1) + 0.001)
    res = short_std - long_std

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    37.67  0.0816
    =====>>>> 37.66666666666667 0.08168381606711933 -0.16553849178177432 0.30662684217089237 Long_short_volatility_diff，skk_TTickab_h2l_std_b 0.6764，0.6029
    """
    return pd.Series(factor_dict)