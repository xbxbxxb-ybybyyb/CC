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


import decimal
import numpy as np


def round_(x, n=0):
    if np.isnan(x):
        return np.nan
    x = x + 1e-8
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))), rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

def factor_fc_trans_20231130_7(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # -------------------------------------------------主买大单中黄线上下平均价格之比--------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 1}

    dt, Ticker = df.index[0]
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
    ZT_Time = df['MDTime'].max()
    pre_close = df['pre_close'].iloc[0]
    df = df.query('TradeType == 0 & TradePrice > 0')
    df['TradeBSFlag'] = (df['TradeBuyNo'] > df['TradeSellNo']).astype(int)
    vwap = round_(df['TradeMoney'].sum() / (df['TradeQty'].sum() + 1), 6)
    df['up_close'] = (df['TradePrice'] > pre_close).astype(int)
    df['up_vwap'] = (df['TradePrice'] > vwap).astype(int)
    df = df.query(f'TradeBSFlag == 1')  # 主动买

    start_time1 = max(fun_get_time(ZT_Time, -3600), 93000000)
    start_time2 = max(fun_get_time(ZT_Time, -6000), 93000000)
    part_df1 = df.query(f'TradeMoney >= 200000 & MDTime >= {start_time1}')
    part_df2 = df.query(f'TradeMoney >= 200000 & {start_time2} >= MDTime >= {start_time1}')

    def calc_res(df_):
        up_vwap = df_.query('up_vwap == 1')
        down_vwap = df_.query('up_vwap == 0')
        up_vwap_px_med = up_vwap['TradePrice'].sum()
        down_vwap_px_med = down_vwap['TradePrice'].sum()
        ret = up_vwap_px_med / (down_vwap_px_med + 1e-5) - 1
        return ret

    res = calc_res(part_df1) - calc_res(part_df2)

    # print(res)
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    42.33 0.079
    =====>>>> 42.333333333333336 0.07953037886660663 20315590.32759439 145805590.0119686 ZT_Time，sss_ZT_Time_ms 0.5308，0.5308
!!!! fc_trans_20231130_2 0.7707184570884257
    """
    return pd.Series(factor_dict)