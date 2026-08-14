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

def factor_fc_LastZtLastTrans_20240314_5(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # ------------------------------------------------------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    pre_close = df.iloc[-1]['pre_close']
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
    target_px = np.floor(pre_close * 1.02 * 100 + 0.5 + 1e-8) / 100 if not zcz else np.floor(pre_close * 1.04 * 100 + 0.5 + 1e-8) / 100

    df = df.query(f'TradeType == 0 & MDTime >= 93000000 & TradePrice != 0 & TradeQty != 0 & TradePrice >= {target_px}')
    df['TradeBSFlag'] = (df['TradeBuyNo'] < df['TradeSellNo']).astype(int) + 1
    sell_group = df.groupby('TradeSellNo')
    buy_group = df.groupby('TradeBuyNo')
    sell_group_sum = sell_group['TradeQty'].sum()
    buy_group_sum = buy_group['TradeQty'].sum()

    act_buy = buy_group['TradeBSFlag'].min() == 1
    act_sell = sell_group['TradeBSFlag'].max() == 2
    if (sell_group_sum[act_sell].sum() + buy_group_sum[act_buy].sum()) != 0:
        res = buy_group_sum[act_buy].sum() / (sell_group_sum[act_sell].sum() + buy_group_sum[act_buy].sum())
    else:
        res = 0
    # res = buy_group_sum[act_buy].mean()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    日内涨幅大于2%的部分，昨日主买成交比例占全部成交量的比值
    =====>>>> 67.708 0.097 0.47137857653376697 0.11772730765287566 Lzt_active_volume_ratio，yzhan_hf_s2_57，Institute_earn，Lzt_big_SB_ratio 0.9857，0.7065，0.6936，0.6643
    """
    return pd.Series(factor_dict)