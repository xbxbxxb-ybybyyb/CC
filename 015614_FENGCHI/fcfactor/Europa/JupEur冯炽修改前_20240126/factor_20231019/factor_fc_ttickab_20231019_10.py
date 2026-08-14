# coding: utf-8
# Author：fengchi863
# Date ：2023/5/10 21:13

import pandas as pd
import numpy as np
import datetime as dt
import decimal

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

def round_(x, n=0):
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

def factor_fc_ttickab_20231019_10(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # ---------------------------------------------------近1小时成交量去除尾部与去除头部后对应vwap的涨跌幅差异------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: -1.0}

    dt, Ticker = df.index[0]
    pre_close = df['pre_close'].iloc[0]
    df = df.query('MDTime >= 93000000')
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')

    if len(df) > 0:
        small, big = df['TotalValueTrade'].quantile([0.4, 0.6])
        small, big = round_(small, 2), round_(big, 2)
        df_small = df[df['TotalValueTrade'] >= small]
        if len(df_small) > 60 * 20: df_small = df_small.head(60 * 20) # clip
        df_big = df[df['TotalValueTrade'] <= big]
        if len(df_big) > 60 * 20: df_big = df_big.head(60 * 20)

        if df_small['TotalValueTrade'].sum() == 0 or df_big['TotalValueTrade'].sum() == 0:
            res = np.nan
        else:
            pct1 = (df_small['TotalValueTrade'].sum() / df_small['TotalVolumeTrade'].sum()) / pre_close - 1 # vwap / pre_close - 1
            pct2 = (df_big['TotalValueTrade'].sum() / df_big['TotalVolumeTrade'].sum()) / pre_close - 1
            res = pct1 - pct2
    else:
        res = np.nan

    if zcz == 1: res = res / 2

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    32.291 0.083
    =====>>>> 32.291666666666664 0.08306610858664087 -0.03623817605993128 0.2057559975187874 wj_TTick_5m_h2prec_std，qyh_ttick_apct_a2b_1m 0.6668，0.6197
    """
    return pd.Series(factor_dict)