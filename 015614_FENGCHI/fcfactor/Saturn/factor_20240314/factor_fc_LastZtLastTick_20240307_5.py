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

def factor_fc_LastZtLastTick_20240307_5(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # ------------------------------------------------------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    pre_close = df.iloc[-1]['pre_close']
    ff_shares = df.iloc[-1]['ff_shares']
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
    df = df.query(f'LastPx != 0')
    df = df.query('93000000 <= MDTime <= 113000000')

    df['tick_volume'] = df['TotalVolumeTrade'] - df['TotalVolumeTrade'].shift().fillna(0)
    order_ratio = df['tick_volume'] / (df[['Buy%dOrderQty' % (j + 1) for j in range(4)]].sum(axis=1) + df[['Sell%dOrderQty' % (j + 1) for j in range(4)]].sum(axis=1))
    order_ratio[np.abs(order_ratio) == np.inf] = 0

    if order_ratio.std() != 0:
        res = order_ratio.std() / order_ratio.mean()
    else:
        res = 0
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    上午委托单比值CV
    =====>>>> 51.042 -0.093 4.94230293050788 4.379438116632709 Lzt_pj2k_sb5_active_mean_std，wd_lzkcs_amt_d_bid_ms_d_m，Institute_earn 0.7952，0.6327，0.6096
    !!!! fc_LastZtLastTick_20240307_3 0.8366466170285295
    """
    return pd.Series(factor_dict)