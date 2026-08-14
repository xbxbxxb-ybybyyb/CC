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

def factor_fc_TallTick_20231229_41(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # ------------------------------------------------------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    pre_close = df.iloc[-1]['pre_close']
    ff_shares = df.iloc[-1]['ff_shares']
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
    df = df.query('130000000 <= MDTime <= 150000000')
    df['TotalVolumeTrade'] = df['TotalVolumeTrade'].diff().fillna(0)
    df['TotalValueTrade'] = df['TotalValueTrade'].diff().fillna(0)
    df['TotalBidQty'] = df['TotalBidQty'].diff().fillna(0)
    df['TotalOfferQty'] = df['TotalOfferQty'].diff().fillna(0)

    seg_threshold = df['TotalOfferQty'].quantile(0.25)
    if len(df) > 0:
        df['Sell8OrderQty'] = df['Sell8OrderQty'].diff().abs().fillna(0)
        part_df1 = df.query(f'TotalOfferQty >= {seg_threshold}')
        part_df2 = df.query(f'TotalOfferQty <= {seg_threshold}')
        if part_df2['Sell8OrderQty'].mean() != 0:
            res = part_df1['Sell8OrderQty'].mean() / part_df2['Sell8OrderQty'].mean()
        else:
            res = 0
    else:
        res = 0
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    买入成交量全天分布截断后不同区间内卖出盘口上委托量的比值
    14.833 0.015
    =====>>>> 14.833333333333334 0.0158297771031559 0.593533491935993 0.40156339282574377 qyh_talltick_rlength_a25_up，qyh_talltick_amt_cct 0.457，0.3809
    """
    return pd.Series(factor_dict)