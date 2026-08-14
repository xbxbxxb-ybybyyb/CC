# coding: utf-8
# Author：fengchi863
# Date ：2023/1/14 23:59

"""
用于制作团队年终述职ppt
"""
from dataApi.tradeDate import get_date_range
from tqdm import tqdm
import pandas as pd
import numpy as np

root_path = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/'
strategy = 'saturn'

date_list = get_date_range(20230101, 20231231)
date_list = get_date_range(20240101, 20241206)
date_list = get_date_range(20230101, 20231215)
# 5.6353 / 2.56 / 225 * 252
# 2.3578 / 1.83 / 232 * 360
profit_list = list()
for _dat in tqdm(date_list):
    daily_profit = pd.read_excel(root_path + f'{strategy}成交记录-{_dat}.xlsx', sheet_name='今日S1汇总情况')
    try:
        daily_sell_profit = daily_profit.iloc[3, 4]
        profit_list.append(daily_sell_profit)
    except:
        print(f'{_dat}没有卖出盈利')
        profit_list.append(0)


profit_s = pd.Series(profit_list, index=date_list)
profit_cumsum = profit_s.cumsum()
from dataApi.sendInfo import send_file
send_file(pd.DataFrame(profit_s))

def calc_mdd(_s):
    mdd = (np.maximum.accumulate(np.nancumsum(_s)) - np.nancumsum(_s)).max()
    return -mdd