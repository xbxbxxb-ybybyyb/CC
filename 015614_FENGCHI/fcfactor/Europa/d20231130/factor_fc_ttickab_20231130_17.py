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

def factor_fc_ttickab_20231130_17(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # -----------------------------------------------------Tick卖出价均值与成交笔数差值均值之比------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
    df['vwap'] = df['TotalValueTrade'] / df['TotalVolumeTrade']
    zt_time = df['MDTime'].max()
    pre_close = df['pre_close'].iloc[0]
    ff_shares = df['ff_shares'].iloc[0]
    df = df.query('MDTime >= 93000000')
    part_df = df.copy()
    part_df['NumTradesDiff'] = part_df['NumTrades'].diff().fillna(0)
    part_df['LastPx'] = (part_df['LastPx'] / pre_close - 1) / (1 + zcz)
    part_df = part_df.query(f'LastPx >= 0.09 & NumTradesDiff > 0')
    part_df['Sell4Price'] = (part_df['Sell4Price'] - pre_close) / pre_close / (1 + zcz)
    res = part_df['Sell4Price'].mean() / part_df['NumTradesDiff'].mean() * 1e5
    if np.isinf(res): res = np.nan

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    38.7 0.075
    =====>>>> 38.708333333333336 0.07534404842902094 -6.801806100677689 1574.1081091211006 xly_t_tick_xb4，xly_t_tick_xb20 0.5969，0.5111
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