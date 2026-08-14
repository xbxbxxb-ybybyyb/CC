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

def cal_time_delta(start, end):
    if np.isnan(start) or np.isnan(end):
        return np.nan
    if start > 120000000:
        start = start - 17000000
    if end > 120000000:
        end = end - 17000000
    start_str = str(int(start))
    end_str = str(int(end))
    time_delta = (int(end_str[:~6]) - int(start_str[:~6])) * 3600000 + \
                 (int(end_str[~6:~4]) - int(start_str[~6:~4])) * 60000 + \
                 (int(end_str[~4:~2]) - int(start_str[~4:~2])) * 1000 + \
                 (int(end_str[~2:]) - int(start_str[~2:]))
    return round(time_delta)

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


def factor_fc_order_20231102_14(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    def calc_res(part1, part2):
        a = np.log(part1['OrderMoney'].sum() + 1)
        b = np.log(part2['OrderMoney'].sum() + 1)
        return a / (b + 0.001)

    if return_fillna_dic:
        return {factor_name: 100}
    # --------------------------------------------------涨停前1分钟最近20笔逐笔委托前后下单买卖金额之比的差值-------------------------------------------------------
    zt_time = int(df.iloc[-1]['MDTime'])
    df = df[df['OrderType'].isin([1, 2])]
    df = df[df['MDTime'] >= 93000000]
    df['OrderMoney'] = df['OrderPrice'] * df['OrderQty']

    start_time = max(fun_get_time(zt_time, -90), 93000000)
    part_df = df.query(f'OrderMoney >= 10000 & MDTime >= {start_time}')

    part_df1 = part_df.iloc[-min(len(part_df), 20):]
    part1_df1 = part_df1.query('OrderBSFlag==1').copy()
    part2_df1 = part_df1.query('OrderBSFlag==2').copy()
    part_df2 = part_df.iloc[:min(len(part_df), 20)]
    part1_df2 = part_df2.query('OrderBSFlag==1').copy()
    part2_df2 = part_df2.query('OrderBSFlag==2').copy()
    res = calc_res(part1_df1, part2_df1) - calc_res(part1_df2, part2_df2)

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    44.33 0.079
    =====>>>> 44.333333333333336 0.07993171845220956 339.93514002857836 2973.8659726115065 skk_order_bs_ratio_t_ratio，skk_order_500_bsr1 0.6296，0.5911
    """
    """
    MDTime: 时间
    OrderIndex: 委托编号：可以在Trans中查询到这个号
    OrderType: 委托类别：1市价2限价
    OrderPrice: 委托价格，对于4、5、6、7会有0的情况，只筛选1和2的，对于市价单设置为涨停跌停价
    OrderQty: 委托数量
    OrderBSFlag: 委托方向，1买2卖
    """
    return pd.Series(factor_dict)