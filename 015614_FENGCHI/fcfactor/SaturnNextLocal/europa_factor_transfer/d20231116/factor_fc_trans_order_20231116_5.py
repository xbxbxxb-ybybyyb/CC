# coding: utf-8
# Author：fengchi863
# Date ：2023/9/6 14:00

import datetime as dt

import numpy as np
import pandas as pd


def fun_get_time(time1, sec_delta):
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

def weight_mean(elements, weights):
    if len(elements) == 0 or len(weights) == 0:
        return 0
    else:
        return np.mean([x*y for x, y in zip(elements, weights)])

def factor_fc_trans_order_20231116_5(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0}
    # -------------------------------------------------突破前20分钟内逐笔委托分钟vwap偏度--------------------------------------------------------
    pre_close = df['pre_close'].max()
    dt, Ticker = df.index[0]
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
    zt_time = int(df.iloc[-1]['MDTime'])
    df = df[df['OrderType'].isin([1, 2])]
    df = df[df['MDTime'] >= 93000000]
    dt_price = np.floor(pre_close * 100 * (0.9 - zcz * 0.1) + 0.5) / 100
    zt_price = np.floor(pre_close * 100 * (1.1 + zcz * 0.1) + 0.5) / 100
    df = df.query(f'OrderPrice <= {zt_price} & OrderPrice >= {dt_price}')
    df['OrderMoney'] = df['OrderPrice'] * df['OrderQty']
    df = df.query('OrderBSFlag==2')  # 卖出
    df['m'] = df['MDTime'] // 1e5

    start_time = max(fun_get_time(zt_time, -1200), 93000000)
    part_df = df.query(f'MDTime >= {start_time}')

    group_df = pd.DataFrame(index=part_df['m'].unique())
    group_df['vwap'] = part_df.groupby('m')['OrderMoney'].sum() / part_df.groupby('m')['OrderQty'].sum()
    group_df['v2pc'] = np.log(group_df['vwap'] / pre_close) * 100
    res = group_df['v2pc'].skew()
    # print(res)
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    36.04 -0.0898
    =====>>>> 31.458333333333336 -0.07253260167982462 0.5587426710286758 0.9307627519713473 qyh_ttick_20230921_10，zwh_20230914_006 0.6811，0.5675
    """
    return pd.Series(factor_dict)