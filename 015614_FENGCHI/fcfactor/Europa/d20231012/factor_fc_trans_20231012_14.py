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


def factor_fc_trans_20231012_14(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # ------------------------------------------------突破前1分钟买单按id分组后量价相关性---------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 1.0}

    df = df[(df['TradeType'] == 0) & (df['TradePrice'] > 0)]
    ZT_Time = df['MDTime'].iloc[-1]

    start_time = max(fun_get_time(ZT_Time, -60), 93000000)
    part_df = df.query(f'MDTime >= {start_time}')
    group_df = part_df.groupby('TradeBuyNo')['TradeMoney', 'TradeQty'].sum()
    group_df['vwap'] = group_df['TradeMoney'] / group_df['TradeQty']
    group_df['TradeQty'] = group_df['TradeQty'].apply(lambda x: np.log(x))

    ret = group_df[['vwap', 'TradeQty']].corr().values[0][1]

    factor_dict = {factor_name: ret}
    # ---------------------------------------------------------------------------------------------------------------
    """
    53.04 0.102
    =====>>>> 53.04166666666667 0.10244732455267991 0.13833890991120226 0.21253461173903854 t_l1_order_time_bda，fc_trans_20230928_18 0.6849，0.6127
    """
    return pd.Series(factor_dict)