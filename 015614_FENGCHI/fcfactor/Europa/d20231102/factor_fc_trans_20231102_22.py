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

def factor_fc_trans_20231102_22(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # --------------------------------------------------涨停前小区间与大区间内高低价差的增量-------------------------------------------------------
    def calc_res(df, zcz):
        if len(df) == 0:
            return 0
        tmp_res = df['TradePrice'].max() / df['TradePrice'].min() - 1
        if zcz: tmp_res /= 2
        return tmp_res

    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    ZT_Time = df['MDTime'].max()
    pre_close = df['pre_close'].iloc[0]
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
    df = df.query('TradeType == 0 & TradePrice > 0')
    # df['TradeBSFlag'] = (df['TradeBuyNo'] > df['TradeSellNo']).astype(int)

    start_time = max(fun_get_time(ZT_Time, -7200), 93000000)
    part_df = df.query(f'MDTime >= {start_time}')

    part_df1 = part_df.iloc[-min(len(part_df), 20):]
    part_df2 = part_df.iloc[:min(len(part_df), 20)]
    res = calc_res(part_df1, zcz) - calc_res(part_df2, zcz)

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    34.5 -0.0854
    =====>>>> 34.5 -0.08545133497923679 0.00021459369214359448 0.008761761351773631 sss_purturn1，xbc_20231019_9 0.3201，0.3054
    !!!! fc_trans_20231102_20 0.7447655073775589
    """
    return pd.Series(factor_dict)