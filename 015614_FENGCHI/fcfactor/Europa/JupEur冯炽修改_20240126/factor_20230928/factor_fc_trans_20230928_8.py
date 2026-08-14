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


def factor_fc_trans_20230928_8(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0}

    # ---------------------------------------------倒数第5笔卖单之后的最大买单对应换手------------------------------------------------------------
    dt, Ticker = df.index[0]
    ff_shares = df['ff_shares'].iloc[0]
    df = df[df['TradeMoney'] > 0]
    df['buy_flag'] = (df['TradeBuyNo'] > df['TradeSellNo']).astype(float)
    df = df[df['MDTime'] >= 93000000]

    sell_df = df[df['buy_flag'] == 0]
    group_sell_df = sell_df.groupby('TradeSellNo').agg({'TradeMoney': sum,
                                                        'TradeIndex': max})  # 去除散户
    mid_big_group_sell = group_sell_df.query(f'TradeMoney > 0')
    last_index = mid_big_group_sell['TradeIndex'].iloc[-5] if len(mid_big_group_sell) >= 5 else 0
    last_buy = df[df['TradeIndex'] > last_index] if len(sell_df) != 0 else df

    if len(last_buy) == 0:
        ret = 0
    else:
        buy_deal_qty_max = last_buy.groupby('TradeBuyNo')['TradeQty'].sum().max()
        ret = buy_deal_qty_max / ff_shares / 1e4  # 最后最大买单的换手

    factor_dict = {factor_name: ret}
    """
    95.625 0.1242
    =====>>>> 95.625 0.12422534420536843 0.0006299764084251205 0.0011221154399920078 sss_turnsum_b10_p7，sss_purturn1，t_l5_old_ask_frate，t_l1_last_up_vol_pct，xbc_dir_money 0.8599，0.7527，0.7111，0.6051，0.6029
    踢馆
    """
    return pd.Series(factor_dict)