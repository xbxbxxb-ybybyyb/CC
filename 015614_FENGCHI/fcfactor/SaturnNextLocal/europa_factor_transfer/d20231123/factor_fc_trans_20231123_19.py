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

def factor_fc_trans_20231123_19(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # -------------------------------------------------突破前两分钟内逐笔成交中主买单数量/主卖单数量--------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 1}

    dt, Ticker = df.index[0]
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
    ZT_Time = df['MDTime'].max()
    pre_close = df['pre_close'].iloc[0]
    df = df.query('TradeType == 0 & TradePrice > 0')
    df['TradeBSFlag'] = (df['TradeBuyNo'] > df['TradeSellNo']).astype(int)

    start_time1 = max(fun_get_time(ZT_Time, -10), 93000000)
    start_time2 = max(fun_get_time(ZT_Time, -90), 93000000)
    part_df1 = df.query(f'MDTime >= {start_time1}')
    part_df2 = df.query(f'{start_time2} >= MDTime >= {start_time1}')

    def calc_res(df_):
        if df_.query('TradeBSFlag == 1').shape[0] == 0 or df_.query('TradeBSFlag == 0').shape[0] == 0:
            ret = 1
        else:
            ret = df_.query('TradeBSFlag == 1').shape[0] / df_.query('TradeBSFlag == 0').shape[0]
        return ret

    res = calc_res(part_df1) - calc_res(part_df2)

    # print(res)
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    59.875 0.1076
    =====>>>> 59.875 0.10767391311480996 17.51030456614212 41.34189949826543 Trick_sell_rate_10000，skk_TTrans_order_100_bs_m 0.6884，0.6763
    """
    return pd.Series(factor_dict)