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

def factor_fc_LastZtLastTick_20240307_1(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # ------------------------------------------------------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    pre_close = df.iloc[-1]['pre_close']
    ff_shares = df.iloc[-1]['ff_shares']
    df = df.query('MDTime >= 93000000')
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
    zt_price = df['LastPx'].max()
    zt_time = df[df['LastPx'] == zt_price]['MDTime'].min()
    df = df.query(f'LastPx != 0')
    df1 = df.query('MDTime >= 93000000')
    zt_time_end = fun_get_time(zt_time, 1200)
    df2 = df.query(f'{zt_time} <= MDTime <= {zt_time_end}')

    if len(df) >= 1:
        after_zt_amt = (df2['TotalBidQty'] * df2['WeightedAvgBidPx']).head(1).sum()
    else:
        after_zt_amt = (df2['TotalBidQty'] * df2['WeightedAvgBidPx']).sum()

    value_max = df1['TotalValueTrade'].max()
    if value_max != 0:
        res = after_zt_amt / value_max
    else:
        res = 0

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    
    =====>>>> 56.083 -0.081 1.8782570591265866 3.9168478641198234 qyh_lzttick_bamt_a1zt2tttl_30s，Lzt_pj2k_cs_avg_fb_volume_ratio_3，qyh_lzo_b_9bs_l 0.9612，0.6538，0.6505
    """
    return pd.Series(factor_dict)