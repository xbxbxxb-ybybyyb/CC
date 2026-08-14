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

def factor_fc_TallTick_20231130_9(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # -------------------------------------------------涨跌幅与成交额一阶差分比值----------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
    zt_time = df['MDTime'].max()
    pre_close = df['pre_close'].iloc[0]
    ff_shares = df['ff_shares'].iloc[0]
    df = df.query('MDTime >= 93000000')
    start_time = max(fun_get_time(zt_time, -14400), 93000000)
    part_df = df.query(f'MDTime >= {start_time}')
    part_df['TotalValueTradeDiff'] = part_df['TotalValueTrade'].diff().fillna(0)
    part_df['WeightedAvgOfferPx'] = (part_df['WeightedAvgOfferPx'] / pre_close - 1) / (1 + zcz)
    part_df = part_df.query(f'WeightedAvgOfferPx >= 0.07')
    part_df['pct_sell9'] = (part_df['Sell9Price'] - pre_close) / pre_close / (1 + zcz)
    part_df = part_df.query(f'TotalValueTradeDiff > 0')
    res = part_df['pct_sell9'].mean() / part_df['TotalValueTradeDiff'].mean() * 1e5
    if np.isinf(res): res = np.nan

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    60.5 0.1068
    =====>>>> 60.50000000000001 0.10681704269588335 0.02416101659828541 0.2029870991191103 xly_t_tick_xb5，wj_TTick_10_h2prec_max7 0.6677，0.656
    eur2mimas:
    15.37 0.054 
    =====>>>> 15.375000000000002 0.05442033872721887 0.017243013482541748 0.06867402639897971 qyh_talltick_sp_mean，zwh_20231207_029 0.4999，0.4698
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