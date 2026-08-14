# coding: utf-8
# Author：fengchi863
# Date ：2023/3/23 15:36

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


def factor_fc_b_deal_pct_60(transaction_df, return_fillna_dic=False):
    factor_name = 'fc_b_deal_pct_60'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    transaction_df = transaction_df[(transaction_df['TradePrice'] > 0)]  # 去除撤单
    transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000]

    ul_time = transaction_df.iloc[-1]['MDTime']
    target_time = fun_get_time(int(ul_time), -60)
    transaction_df = transaction_df.query(f'MDTime >= {target_time}')
    big_deal_df = transaction_df.query('TradeMoney > 200000')
    if big_deal_df.shape[0] != 0:
        ret = big_deal_df['TradeMoney'].sum() / transaction_df['TradeMoney'].sum()
    else:
        ret = 0

    factor = ret
    factor_dict = {factor_name: factor}

    return pd.Series(factor_dict)