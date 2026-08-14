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

def factor_fc_trans_20231102_21(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # --------------------------------------------------突破前短区间内trans主买金额占比相对于全天主买金额占比的变化-------------------------------------------------------
    def calc_res(df):
        if len(df) == 0:
            return 0
        return df.query('TradeBSFlag == 1')['TradeQty'].sum() / df['TradeQty'].sum()

    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    ZT_Time = df['MDTime'].max()
    pre_close = df['pre_close'].iloc[0]
    df = df.query('TradeType == 0 & TradePrice > 0')
    df['TradeBSFlag'] = (df['TradeBuyNo'] > df['TradeSellNo']).astype(int)

    start_time = max(fun_get_time(ZT_Time, -120), 93000000)
    part_df = df.query(f'TradeMoney >= 10000 & MDTime >= {start_time}')

    part_df1 = part_df.iloc[-min(len(part_df), 50):]
    part_df2 = part_df.iloc[:min(len(part_df), 50)]
    res = calc_res(part_df1) - calc_res(part_df2)

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    39.625 0.067
    =====>>>> 39.62500000000001 0.0670121878848684 0.15502852350131724 0.2533842550290307 fc_trans_20231026_5，fc_trans_order_20230928_12 0.5439，0.4886
    """
    return pd.Series(factor_dict)