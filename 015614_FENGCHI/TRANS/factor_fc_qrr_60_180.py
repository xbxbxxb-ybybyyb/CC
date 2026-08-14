# coding: utf-8
# Author：fengchi863
# Date ：2023/3/23 14:59

import pandas as pd
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


def factor_fc_qrr_60_180(transaction_df, return_fillna_dic=False):
    factor_name = 'fc_qrr_60_180'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    transaction_df = transaction_df[(transaction_df['TradePrice'] > 0)]  # 去除撤单
    transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000]

    ul_time = transaction_df.iloc[-1]['MDTime']
    time60s = fun_get_time(int(ul_time), -60)
    time180s = fun_get_time(int(ul_time), -180)
    transaction_df1 = transaction_df.query(f'MDTime >= {time60s}')
    transaction_df2 = transaction_df.query(f'MDTime >= {time180s}')
    ret = transaction_df1['TradeMoney'].sum() / 60 / ((transaction_df2['TradeMoney'].sum() - transaction_df1['TradeMoney'].sum()) / 120)

    factor = ret
    factor_dict = {factor_name: factor}

    return pd.Series(factor_dict)