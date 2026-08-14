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

def factor_fc_trans_20231019_12(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # --------------------------------------------------突破前10分钟按卖单vwap与单号rank的相关性-------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    df = df.query('MDTime >= 93000000')
    ZT_Time = df['MDTime'].max()
    df = df[(df['TradeType'] == 0) & (df['TradePrice'] > 0)]

    start_time = max(93000000, fun_get_time(ZT_Time, -600))
    df = df[df['MDTime'] >= start_time]
    group_df = df.groupby('TradeSellNo')['TradeMoney', 'TradeQty'].sum()
    group_df['vwap'] = group_df['TradeMoney'] / group_df['TradeQty']
    group_df = group_df.reset_index()
    group_df['TradeSellNo'] = group_df['TradeSellNo'].rank()
    res = group_df[['vwap', 'TradeSellNo']].corr().values[0][1]

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    45.83 -0.067
    =====>>>> 45.833333333333336 -0.06716759658779732 -0.029441766856215922 0.3954515906807084 skk_TTickab_LPR_roll2vwap_std_a，qyh_ttick_20231012_7 0.6501，0.6482
    """
    return pd.Series(factor_dict)