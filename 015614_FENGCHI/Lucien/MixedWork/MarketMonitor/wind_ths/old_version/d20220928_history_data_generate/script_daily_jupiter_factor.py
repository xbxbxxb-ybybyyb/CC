# coding: utf-8
# Author：fengchi863
# Date ：2022/9/19 9:08
from dataApi import tradeDate
import os

start_date = 20220913
end_date = 20220916
date_list = tradeDate.get_date_range(start_date, end_date)

code_root_path = '/data/user/015614/Lucien/MixedWork/MarketMonitor/wind_ths/history_data_generate/'

for dat in date_list:
    os.system(f'python3 timer_daily_jupiter_factor.py {dat}')

