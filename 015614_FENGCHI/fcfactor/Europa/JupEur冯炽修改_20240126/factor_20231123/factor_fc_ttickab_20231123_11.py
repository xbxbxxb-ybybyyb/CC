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

def factor_fc_ttickab_20231123_11(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # --------------------------------------------------涨停前10分钟内不同区间段内vwap的均值变化率---------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 1000}

    dt, Ticker = df.index[0]
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
    zt_time = df['MDTime'].max()
    pre_close = df['pre_close'].iloc[0]
    ff_shares = df['ff_shares'].iloc[0]
    df = df.query('MDTime >= 93000000')
    df['m'] = df['MDTime'].astype(str).map(lambda x: x[:-4])

    start_time1 = max(fun_get_time(zt_time, -180), 93000000)
    start_time2 = max(fun_get_time(zt_time, -600), 93000000)
    part_df1 = df.query(f'MDTime >= {start_time1}')
    part_df2 = df.query(f'{start_time1} >= MDTime >= {start_time2}')

    def calc_res(df_):
        group_df_px = df_.groupby('m')['Buy1Price'].mean() / pre_close - 1
        group_df_qty = df_.groupby('m')['TotalBidQty'].mean() / ff_shares
        return (group_df_px / group_df_qty).mean()

    res = calc_res(part_df1) / (calc_res(part_df2) + 1e-4)
    # print(res)
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    30.20 -0.067
    =====>>>> 30.208333333333336 -0.0675679601372253 inf nan xbc_20230914_13，xbc_20230914_12 0.5696，0.5188
    """
    """
    MDTime: 时间 如101215000
    TradeBSFlag：不用这个
    TradeIndex：成交编号，与OrderIndex可匹配
    TradeBuyNo：买方委托序号 TradeBuyNo > TradeSellNo 主动买入 否则被动买入
    TradeSellNo：卖方委托序号
    # 以上委托序号与OrderIndex相同
    TradeType：成交类别
    TradeBSFlag：成交方向 1买 2卖
    TradePrice：成交价格
    TradeQty：成交数量
    TradeMoney：成交金额，等于0是撤单的股票
    pre_close：昨收价
    ff_shares：流通股数
    """
    return pd.Series(factor_dict)