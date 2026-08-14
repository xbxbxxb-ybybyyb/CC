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

def factor_fc_trans_20231019_6(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # ------------------------------------------------突破前90秒大于价格中位值部分的vwap与卖单号秩相关性---------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: -1.0}

    df = df.query('TradeType == 0 & TradePrice > 0')
    ZT_Time = df['MDTime'].iloc[-1]

    start_time = max(93000000, fun_get_time(ZT_Time, -90))
    df = df.query(f'MDTime > {start_time}')
    mid_price = np.median(np.unique(df['TradePrice']))
    part_df = df.query(f'TradePrice >= {mid_price}').copy()
    part_df = part_df.groupby('TradeSellNo').sum()[['TradeMoney', 'TradeQty']]
    part_df['vwap'] = part_df['TradeMoney'] / part_df['TradeQty']

    res = part_df.reset_index()[['vwap', 'TradeSellNo']].corr(method='spearman').values[0][1]

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    68.75 -0.09491
    =====>>>> 68.75 -0.09490510615906161 -0.18153705537437567 0.2324620735390211 wwd_t_up_half_ask_corr_pid，wwd_t1_ask_corrh_pid 0.5993，0.5464
    """
    return pd.Series(factor_dict)