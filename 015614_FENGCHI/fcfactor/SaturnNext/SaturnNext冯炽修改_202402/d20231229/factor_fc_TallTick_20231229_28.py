# coding: utf-8
# Author：fengchi863
# Date ：2023/5/10 21:13

import pandas as pd
import numpy as np
import datetime as dt
import decimal
def round_(x, n=0):
    x = x + 1e-8
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

def factor_fc_TallTick_20231229_28(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # ------------------------------------------------------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    pre_close = df.iloc[-1]['pre_close']
    ff_shares = df.iloc[-1]['ff_shares']
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
    df = df.query('93000000 <= MDTime <= 113000000')
    df['TotalVolumeTrade'] = df['TotalVolumeTrade'].diff().fillna(0).apply(lambda x: round_(x, 6))
    df['TotalValueTrade'] = df['TotalValueTrade'].diff().fillna(0).apply(lambda x: round_(x, 6))
    df['TotalBidQty'] = df['TotalBidQty'].diff().fillna(0).apply(lambda x: round_(x, 6))
    df['TotalOfferQty'] = df['TotalOfferQty'].diff().fillna(0).apply(lambda x: round_(x, 6))

    seg_threshold = round_(df['TotalValueTrade'].quantile(0.9), 6)
    if len(df) > 0:
        df['Buy1NumOrders'] = df['Buy1NumOrders'].diff().abs().fillna(0).apply(lambda x: round_(x, 6))
        part_df1 = df.query(f'TotalValueTrade >= {seg_threshold}')
        part_df2 = df.query(f'TotalValueTrade <= {seg_threshold}')
        res = np.divide(part_df1['Buy1NumOrders'].mean(), part_df2['Buy1NumOrders'].mean())
        if np.isinf(res):
            res = 0
    else:
        res = 0
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    全天成交额分区后买一委托下单笔数的平均的比率
    17.75 -0.0457
    =====>>>> 17.75 -0.0457518760591288 3.299138250261731 9.59019130286474 qyh_talltick_rlength_a25_up，qyh_talltick_amt_cct 0.4509，0.4318
    """
    return pd.Series(factor_dict)