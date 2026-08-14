# @Time : 2021/5/12 20:22
# @Author : Zhichen Lu
# @File : inital_strategy.py

import pandas as pd
import os
from online_conf import local_config_path, path_for_930


def initial_930_startegy(cash_start, start_date, pre_date, barly_max_buy, stk_min_amt, per_signal_ratio, order_ratio):
    if not os.path.exists(f'{local_config_path}/FolderFor930/{start_date}/'):
        os.mkdir(f'{local_config_path}/FolderFor930/{start_date}/')
        os.mkdir(f'{local_config_path}/FolderFor930/{start_date}/StrategyOut/')
        os.mkdir(f'{local_config_path}/FolderFor930/{start_date}/StrategyIn/')
    if not os.path.exists(f'{local_config_path}/FolderFor930/{pre_date}/'):
        os.mkdir(f'{local_config_path}/FolderFor930/{pre_date}/')
        os.mkdir(f'{local_config_path}/FolderFor930/{pre_date}/StrategyOut/')
        os.mkdir(f'{local_config_path}/FolderFor930/{pre_date}/StrategyIn/')
    pd.to_pickle({'cash': cash_start}, f'{local_config_path}/FolderFor930/{pre_date}/StrategyOut/holding{pre_date}.pkl')
    pd.to_pickle({}, f'{local_config_path}/FolderFor930/{pre_date}/StrategyOut/buy_time_info{pre_date}.pkl')
    # if not os.path.exists(f'/data/group/800319/strategy_local_path3/FolderFor930/{start_date}/StrategyIn/init{start_date}.pkl'):
    per_amt = max(cash_start * per_signal_ratio // 10000 * 10000, 10000)
    conf = {
        'date': start_date,
        'pre_date': pre_date,
        'barly_max_buy': barly_max_buy,
        'stk_min_amt': int(min(stk_min_amt * per_amt, 500000)),
        'per_amt': per_amt,
        'cash': cash_start,
        'portfolio_id': '201001',
        'order_ratio': order_ratio
    }
    pd.to_pickle(conf, f'{path_for_930}/{start_date}/StrategyIn/init{start_date}.pkl')
    print(conf)
    pd.to_pickle({'account_value': cash_start, 'holding_num': 0}, f'{path_for_930}/{start_date}/StrategyIn/account_info{start_date}.pkl')


import datetime
from dataApi.tradeDate import get_pre_trade_date
if __name__ == '__main__':

    date = 20210701  # int(datetime.date.today().strftime('%Y%m%d'))
    next_day = get_pre_trade_date(date, -1)
    print(next_day, date)
    initial_930_startegy(1000000, next_day, date, barly_max_buy=100, stk_min_amt=0.2, per_signal_ratio=0.015, order_ratio=0.1)



