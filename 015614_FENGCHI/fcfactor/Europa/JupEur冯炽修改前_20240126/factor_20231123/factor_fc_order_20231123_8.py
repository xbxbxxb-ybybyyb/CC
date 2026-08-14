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


def factor_fc_order_20231123_8(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0}
    # --------------------------------------------------近20秒与近2分钟逐笔委托中卖出价中位值的前后变化差异-------------------------------------------------------
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

    start_time1 = max(fun_get_time(zt_time, -20), 93000000)
    start_time2 = max(fun_get_time(zt_time, -120), 93000000)
    part_df1 = df.query(f'MDTime >= {start_time1}')
    part_df2 = df.query(f'{start_time1} >= MDTime >= {start_time2}')

    def calc_res(df_):
        return df_['OrderPrice'].median() if len(df_) != 0 else 0

    res = calc_res(part_df1) / (calc_res(part_df2) + 1e-3) - 1
    # print(res)
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    37.67 -0.0927
    =====>>>> 37.66666666666667 -0.09277397714268017 209.93423956868364 2276.2067978668415 fc_trans_20231019_3，skk_TTickab_h2l_std_b 0.6864，0.6685
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