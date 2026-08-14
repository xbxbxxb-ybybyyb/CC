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

def factor_fc_ttickab_20231123_21(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # -------------------------------------------------涨停前20分钟内均买价占TickK柱相对于突破前的变化率----------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 1000}

    dt, Ticker = df.index[0]
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
    zt_time = df['MDTime'].max()
    pre_close = df['pre_close'].iloc[0]
    ff_shares = df['ff_shares'].iloc[0]
    df = df.query('MDTime >= 93000000')

    start_time1 = max(fun_get_time(zt_time, -20), 93000000)
    start_time2 = max(fun_get_time(zt_time, -1200), 93000000)
    part_df1 = df.query(f'MDTime >= {start_time1}')
    part_df2 = df.query(f'{start_time1} >= MDTime >= {start_time2}')

    def calc_res(df_):
        ret = ((df_['WeightedAvgOfferPx'] - df_['LowPx'] + 0.0001) / (df_['HighPx'] - df_['LowPx'] + 1e-4)).sum()
        return ret

    res = calc_res(part_df1) / (calc_res(part_df2) + 1e-4)
    # print(res)
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    51.54 0.074
    =====>>>> 51.54166666666667 0.07439539252271385 22088.85698204088 1425246.8726833148 zwh_20230914_005，qyh_ttick_20231026_1 0.5404，0.5261
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