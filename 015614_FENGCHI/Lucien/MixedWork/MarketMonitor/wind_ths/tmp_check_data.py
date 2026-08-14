# coding: utf-8
# Author：fengchi863
# Date ：2022/9/6 21:30

import pandas as pd
from dataApi.tradeDate import get_date_range

block_path = '/data/user/015614/daily/basic/basic_wind_sw_history/BlockData/daily_max_pctchg_concept/'

start_date = 20160101
end_date = 20220915
date_list = get_date_range(start_date, end_date)
for dat in date_list:
    check = pd.read_pickle(block_path + f'{dat}.pkl')
    if '概念涨停数量' not in check.columns.tolist():
        print(2)
    else:
        if check['概念涨停数量'].min() == 0:
            print(2)

trade_date = 20220906
check = pd.read_pickle('/data/user/015614/daily/basic/basic_wind_sw_history/BlockData/sw2021_each_block/801995.SI.pkl')
check = pd.read_pickle(block_path + f'daily_max_pctchg_concept/{trade_date}.pkl')
check = pd.read_excel('/data/user/015614/junkData/申万二级行业数据.xlsx')
pass

from dataApi import getData
check = getData.get_daily_1factor('high', date_list=[20160714], code_list=[748])