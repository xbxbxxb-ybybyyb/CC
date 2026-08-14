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

def factor_fc_trans_order_20231116_4(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0}
    # -------------------------------------------------涨停前20分钟内逐笔中单委托分钟vwap偏度--------------------------------------------------------
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

    start_time = max(fun_get_time(zt_time, -6000), 93000000)
    part_df = df.query(f'OrderMoney >= 50000 & MDTime >= {start_time}')

    group_df = pd.DataFrame(index=part_df['m'].unique())
    group_df['vwap'] = part_df.groupby('m')['OrderMoney'].sum() / part_df.groupby('m')['OrderQty'].sum()
    group_df['v2pc'] = np.log(group_df['vwap'] / pre_close) * 100
    res = group_df['v2pc'].skew()
    # print(res)
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    64.33 -0.11
    =====>>>> 50.54166666666667 -0.0932944812677891 0.3983687677590264 0.9238903627470889 zwh_20230914_007，xbc_20231012_6 0.6797，0.6282
    """
    return pd.Series(factor_dict)