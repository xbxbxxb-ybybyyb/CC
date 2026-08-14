# coding: utf-8
# Author：fengchi863
# Date ：2023/3/13 15:34

"""
过去30s买单集中度因子
"""
import datetime as dt
import numpy as np
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
def factor_fc_conc_ratio_30s(transaction_df, return_fillna_dic=False):
    factor_name = 'fc_conc_ratio_30s'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]  # 去除深圳撤单的逐笔成交数据
    transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000]  # 选择连续竞价阶段的逐笔成交数据
    transaction_df = transaction_df.query('TradeBuyNo > TradeSellNo')  # 筛选买单数据

    # 过去30秒买单集中度因子
    if transaction_df.shape[0] == 0:
        factor = np.nan
    else:
        ul_time = transaction_df.iloc[-1]['MDTime']
        target_time = fun_get_time(int(ul_time), -30)
        transaction_df = transaction_df.query(f'MDTime >= {target_time}')
        factor = (transaction_df['TradeMoney'] ** 2).sum() / transaction_df['TradeMoney'].sum() ** 2

    factor_dict = {factor_name: factor}
    return pd.Series(factor_dict)


if __name__ == '__main__':
    import IO
    start_date, end_date=20160101, 20181231
    factor_df=factor_fc_conc_ratio_30s(start_date,end_date,IO)
    factor_path = '/data/user/015614/factor/'
    factor_df.to_hdf(factor_path + 'fc_conc_ratio_30s.h5', key='fc_conc_ratio_30s', mode='w')
    print(factor_df.describe())