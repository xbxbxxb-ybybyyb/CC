# coding: utf-8
# Author：fengchi863
# Date ：2023/5/10 21:13

import pandas as pd
import numpy as np
import datetime as dt

def generate_group(df, group_num=10):
    _df = df.copy()
    element_num = len(df) // group_num
    group_id_list = list()
    for i in range(group_num):
        if i != group_num - 1:
            group_id_list.extend([i] * element_num)
        else:
            group_id_list.extend([i] * (len(_df) - element_num * (group_num - 1)))
    _df['group_id'] = group_id_list
    return _df

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


def factor_fc_order_20230914_14(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0}

    # ----------------------------------------------------突破前30秒逐笔委托头尾区间委托量比例-----------------------------------------------------
    zt_time = int(df.iloc[-1]['MDTime'])
    df = df[df['OrderType'].isin([1, 2])]
    df = df[df['MDTime'] >= 93000000]

    df = df[df['MDTime'] >= max(fun_get_time(zt_time, -30), 93000000)]
    df = generate_group(df, group_num=20)
    group_df = df.groupby('group_id')['OrderQty'].sum()
    factor = group_df.tail(2).sum() / group_df.head(2).sum()
    factor_dict = {factor_name: factor}
    # --------------------------------------------------------33.75 0.07488-------------------------------------------------------
    """
    MDTime: 时间
    OrderIndex: 委托编号：可以在Trans中查询到这个号
    OrderType: 委托类别：1市价2限价
    OrderPrice: 委托价格，对于4、5、6、7会有0的情况，只筛选1和2的，对于市价单设置为涨停跌停价
    OrderQty: 委托数量
    OrderBSFlag: 委托方向，1买2卖
    """
    return pd.Series(factor_dict)