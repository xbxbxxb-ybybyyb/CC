# coding: utf-8
# Author：fengchi863
# Date ：2023/3/14 13:14

"""
转换为tick数据，主买金额mean/std，计算涨停前1min净主买强度
"""
import datetime as dt

import pandas as pd


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

#TTransaction(逐笔成交类因子)示例 Todo:注意TTransaction类因子需要控制低耗时
def factor_fc_net_buy_str_1m(transaction_df, return_fillna_dic=False):
    factor_name = 'fc_net_buy_str_1m'

    if return_fillna_dic:
        return {factor_name: 0}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]  # 去除深圳撤单的逐笔成交数据
    transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000]  # 选择连续竞价阶段的逐笔成交数据
    transaction_df['TradeMoney'] = transaction_df['TradePrice'] * transaction_df['TradeQty']

    ul_time = transaction_df.iloc[-1]['MDTime']
    target_time = fun_get_time(int(ul_time), -60)
    transaction_df = transaction_df.query(f'MDTime >= {target_time}')

    transaction_df['raw_tick'] = transaction_df['MDTime'] // 1000
    transaction_df['tick'] = transaction_df['raw_tick'] // 100 * 100 + transaction_df['raw_tick'] % 100 - transaction_df['raw_tick'] % 100 % 3

    transaction_buy = transaction_df.query('TradeBuyNo > TradeSellNo')   # 筛选买单数据
    transaction_sell = transaction_df.query('TradeBuyNo < TradeSellNo')   # 筛选卖单数据

    transaction_buy_tick = transaction_buy.groupby('tick')['TradeMoney'].sum()
    transaction_sell_tick = transaction_sell.groupby('tick')['TradeMoney'].sum()
    transaction_net_buy_tick = transaction_buy_tick - transaction_sell_tick

    if transaction_net_buy_tick.std() != 0:
        factor = transaction_net_buy_tick.mean() / transaction_net_buy_tick.std()   # 这里要设置天充值，填充为最大值
    else:
        factor = 20

    factor_dict = {factor_name: factor}
    return pd.Series(factor_dict)

if __name__ == '__main__':
    import IO
    start_date, end_date=20160101, 20181231
    factor_df=factor_fc_net_buy_str_1m(start_date,end_date,IO)
    factor_path = '/data/user/015614/factor/'
    factor_df.to_hdf(factor_path + 'fc_net_buy_str_1m.h5', key='fc_net_buy_str_1m', mode='w')
    print(factor_df.describe())