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

def factor_fc_trans_20231026_3(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # --------------------------------------------------突破前30分钟大于价格中位值部分的vwap与买单号秩相关性-------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: -1.0}

    df = df.query('TradeType == 0 & TradePrice > 0')
    ZT_Time = df['MDTime'].iloc[-1]

    start_time = max(93000000, fun_get_time(ZT_Time, -1800))
    df = df.query(f'MDTime > {start_time}')
    mid_price = np.median(np.unique(df['TradePrice']))
    part_df = df.query(f'TradePrice >= {mid_price}').copy()
    part_df = part_df.groupby('TradeBuyNo').sum()[['TradeMoney', 'TradeQty']]
    part_df['vwap'] = part_df['TradeMoney'] / part_df['TradeQty']

    res = part_df.reset_index()[['vwap', 'TradeBuyNo']].corr(method='spearman').values[0][1]

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    47.41 -0.077
    =====>>>> 47.416666666666664 -0.07703776218052752 0.575156916210787 0.44860858719531366 wwd_t1_ask_corrh_pid，wj_TTick_1m_c2h_info 0.4979，0.4837
    """
    return pd.Series(factor_dict)