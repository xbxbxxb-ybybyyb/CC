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

def factor_fc_ttickab_20231109_10(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # ---------------------------------------------买一价对应涨跌幅两段区间内的均值之差---------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 0}

    def calc_res(part_df):
        _part_df = part_df.copy()
        if len(part_df) == 0: return 0
        _part_df['pctchg'] = (_part_df['Buy1Price'] / pre_close - 1) / (zcz + 1)
        ret = _part_df['pctchg'] / (_part_df['TotalBidQty'] + 1)
        return ret.mean() * 1e6

    dt, Ticker = df.index[0]
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
    ZT_Time = df['MDTime'].max()
    pre_close = df['pre_close'].iloc[0]
    df = df[df['MDTime'] >= 93000000]

    part_df1 = df.iloc[:min(len(df) // 3 * 2, len(df) - 600)]
    part_df2 = df.iloc[-min(len(df), 600):]
    res = calc_res(part_df1) * calc_res(part_df2)

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    53.20 0.095
    =====>>>> 53.208333333333336 0.0951165643131423 69438.96702559943 10142911.622036798 xly_t_tick_pqd51，wj_TTick_pos_pctvol 0.605，0.5964
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