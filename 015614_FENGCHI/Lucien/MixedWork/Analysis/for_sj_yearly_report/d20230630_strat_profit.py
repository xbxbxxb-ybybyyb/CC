# coding: utf-8
# Author：fengchi863
# Date ：2023/6/30 10:46

from dataApi.tradeDate import get_date_range
from tqdm import tqdm
import pandas as pd
import numpy as np
from dataApi.sendInfo import send_file

root_path = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/'
strategy = 'saturn'    # Europa从5.18开始
date_list = get_date_range(20230101, 20241206)

if strategy == 'jupiter':
    profit_list = list()
    tmp_cumsum = 0
    for _dat in tqdm(date_list):
        print(_dat)
        daily_profit = pd.read_excel(root_path + f'{strategy}成交记录-{_dat}.xlsx', sheet_name='今日汇总情况')
        try:
            daily_sell_profit = daily_profit.iloc[20, 1]
            profit_list.append(daily_sell_profit)
            tmp_cumsum += daily_sell_profit
            print(f'{_dat}当天盈利{daily_sell_profit}元，累计盈利{tmp_cumsum}元')
        except:
            print(f'{_dat}没有卖出盈利')
            profit_list.append(0)

    profit_s = pd.Series(profit_list, index=date_list)
    profit_cumsum = profit_s.cumsum()
    send_file(pd.DataFrame(profit_s))
    print('6月份赚：', profit_cumsum)
elif strategy == 'Europa':
    profit_list = list()
    tmp_cumsum = 0
    for _dat in tqdm(date_list):
        print(_dat)
        daily_profit = pd.read_excel(root_path + f'{strategy}成交记录-{_dat}.xlsx', sheet_name='今日汇总情况')
        try:
            daily_sell_profit = daily_profit.iloc[20, 1]
            profit_list.append(daily_sell_profit)
            tmp_cumsum += daily_sell_profit
            print(f'{_dat}当天盈利{daily_sell_profit}元，累计盈利{tmp_cumsum}元')
        except:
            print(f'{_dat}没有卖出盈利')
            profit_list.append(0)

    profit_s = pd.Series(profit_list, index=date_list)
    send_file(pd.DataFrame(profit_s))
    profit_cumsum = profit_s.cumsum()
    print('6月份赚：', profit_cumsum)
elif strategy == 'saturn':
    profit_list = list()
    tmp_cumsum = 0
    for _dat in tqdm(date_list):
        print(_dat)
        daily_profit = pd.read_excel(root_path + f'{strategy}成交记录-{_dat}.xlsx', sheet_name='今日S1汇总情况')
        try:
            daily_sell_profit = daily_profit.iloc[3, 4]
            profit_list.append(daily_sell_profit)
            tmp_cumsum += daily_sell_profit
            print(f'{_dat}当天盈利{daily_sell_profit}元，累计盈利{tmp_cumsum}元')
        except:
            print(f'{_dat}没有卖出盈利')
            profit_list.append(0)

    profit_s = pd.Series(profit_list, index=date_list)
    send_file(pd.DataFrame(profit_s))
    profit_cumsum = profit_s.cumsum()
    print('6月份赚：', profit_cumsum)
