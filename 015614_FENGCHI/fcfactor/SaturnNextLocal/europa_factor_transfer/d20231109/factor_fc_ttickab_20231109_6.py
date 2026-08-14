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

def factor_fc_ttickab_20231109_6(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # ---------------------------------------------突破前三分钟Tick_vwap与均卖价涨跌幅差值std/mean---------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 0.1}

    def calc_res(part_df, p):
        if len(part_df) == 0:
            return 0
        else:
            part_df_ = part_df[part_df['ValueTrade'] >= part_df['ValueTrade'].quantile(p)]
            part_df_ = part_df_.tail(len(part_df2) // 2 + 1)
            part_df_['ret'] = (part_df_['ValueTrade'] / part_df_['VolumeTrade'] - part_df_['WeightedAvgBidPx']) / pre_close
            return part_df_['ret'].std() / (part_df_['ret'].mean() + 1e-4)

    dt, Ticker = df.index[0]
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
    ZT_Time = df['MDTime'].max()
    pre_close = df['pre_close'].iloc[0]
    df = df[df['MDTime'] >= 93000000]
    df['ValueTrade'] = df['TotalValueTrade'].diff().fillna(0)
    df['VolumeTrade'] = df['TotalVolumeTrade'].diff().fillna(0)

    part_df1 = df.iloc[:min(len(df) // 3 * 2, len(df) - 60)]
    part_df2 = df.iloc[-min(len(df), 60):]
    res = calc_res(part_df1, 0.8) - calc_res(part_df2, 0.8)

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    41.41 0.091
    ====>>>> 41.41666666666667 0.09130839875059109 -0.03943731418257159 0.13797728334806636 skk_TTickab_px_wb_diff_std，qyh_ttick_20231026_2 0.6469，0.505
    """
    """
    MDTime: 时间
    WeightedAvgOfferPx：本tick平均买入价
    WeightedAvgBidPx：本tick平均卖出价
    LastPx：最新价
    TotalOfferQty：卖出总量
    TotalBidQty：买入总量
    NumTrades：从开盘到现在成交笔数，切记是总成交，所以要diff()
    """
    return pd.Series(factor_dict)