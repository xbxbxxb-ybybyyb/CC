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

def factor_fc_trans_20231123_15(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # -------------------------------------------------突破前两个区间内涨跌幅绝对值之和的delta--------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 2}

    dt, Ticker = df.index[0]
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
    ZT_Time = df['MDTime'].max()
    pre_close = df['pre_close'].iloc[0]
    df = df.query('TradeType == 0 & TradePrice > 0')
    df['TradeBSFlag'] = (df['TradeBuyNo'] > df['TradeSellNo']).astype(int)

    start_time1 = max(fun_get_time(ZT_Time, -90), 93000000)
    start_time2 = max(fun_get_time(ZT_Time, -120), 93000000)
    part_df1 = df.query(f'TradeMoney >= 100000 & MDTime >= {start_time1}')
    part_df2 = df.query(f'TradeMoney >= 100000 & {start_time2} >= MDTime >= {start_time1}')

    def calc_res(df_):
        df_['pct'] = (df_['TradePrice'] / pre_close - 1) / (zcz + 1)
        df_['pct_abs'] = df_['pct'].diff().abs()
        ret = df_['pct_abs'].dropna().sum()
        return ret

    res = calc_res(part_df1) - calc_res(part_df2)
    # print(res)
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    28.54 -0.0741
    =====>>>> 28.541666666666668 -0.07409655040682105 0.046785823695329264 0.05253125996194698 xbc_up_down_ratio_diff_abs，max_rise_pct 0.6702，0.6124
    """
    return pd.Series(factor_dict)