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

def factor_fc_trans_20231026_4(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # --------------------------------------------------突破前两小时大于价格中位值部分的vwap与买单号秩相关性-------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: -1.0}

    df = df.query('TradeType == 0 & TradePrice > 0')
    ZT_Time = df['MDTime'].iloc[-1]

    start_time = max(93000000, fun_get_time(ZT_Time, -7200))
    df = df.query(f'MDTime > {start_time}')
    mid_price = np.median(np.unique(df['TradePrice']))
    part_df = df.query(f'TradePrice >= {mid_price}').copy()
    part_df = part_df.groupby('TradeBuyNo').sum()[['TradeMoney', 'TradeQty']]
    part_df['vwap'] = part_df['TradeMoney'] / part_df['TradeQty']

    res = part_df.reset_index()[['vwap', 'TradeBuyNo']].corr(method='spearman').values[0][1]

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    40.70 -0.089
    =====>>>> 40.708333333333336 -0.08951920058538401 0.5584182088798888 0.4257253805032172 skk_TTickab_high_px_diff，sss_draw2_vwap 0.4903，0.4345
    """
    return pd.Series(factor_dict)