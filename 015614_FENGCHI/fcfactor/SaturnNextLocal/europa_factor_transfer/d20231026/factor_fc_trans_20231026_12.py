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

def factor_fc_trans_20231026_12(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # ------------------------------------------------突破前5分钟与全天的平均单笔净买入金额的量差------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    ZT_Time = df['MDTime'].max()
    pre_close = df['pre_close'].iloc[0]

    short_start_time = max(93000000, fun_get_time(ZT_Time, -300))
    long_start_time = max(93000000, fun_get_time(ZT_Time, -7200))

    df['buy_flag'] = (df['TradeBuyNo'] > df['TradeSellNo']).replace({True: 1, False: -1})
    df['act_buy_amt'] = df['buy_flag'] * df['TradeMoney']
    res1 = df.query(f'MDTime > {short_start_time}')['act_buy_amt'].mean() / 100
    res2 = df.query(f'MDTime > {long_start_time}')['act_buy_amt'].mean() / 100

    factor_dict = {factor_name: res1 - res2}
    # ---------------------------------------------------------------------------------------------------------------
    """
    41.16 0.073
    =====>>>> 41.16666666666667 0.07317167803847824 53.005053667725615 67.96766467124129 fc_trans_20231019_12，wj_TTick_5m_h2precv_diff 0.6279，0.6205
    """
    return pd.Series(factor_dict)