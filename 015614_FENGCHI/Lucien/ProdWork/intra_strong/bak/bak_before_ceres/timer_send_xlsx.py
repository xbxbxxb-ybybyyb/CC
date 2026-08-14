# coding: utf-8
# Author：fengchi863
# Date ：2023/5/4 21:36
import sys
import os
sys.path.append('/data/user/015614/Lucien')

from dataApi.sendInfo import send_message, send_file
from dataApi.tradeDate import get_today
import pandas as pd
import time

today_date = get_today()
# today_date = 20240930
root_path = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/'

# concept_data = pd.read_pickle('/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/daily_Wind&SW/20230905.pkl')

while True:
    if os.path.exists(root_path + f'Europa成交记录-{today_date}.xlsx') and \
        os.path.exists(root_path + f'jupiter成交记录-{today_date}.xlsx') and \
        os.path.exists(root_path + f'saturn成交记录-{today_date}.xlsx') and \
        os.path.exists(root_path + f'Metis成交记录-{today_date}.xlsx') and \
        os.path.exists(root_path + f'Leda成交记录-{today_date}.xlsx'):

        send_file(root_path + f'Europa成交记录-{today_date}.xlsx')
        send_file(root_path + f'jupiter成交记录-{today_date}.xlsx')
        send_file(root_path + f'saturn成交记录-{today_date}.xlsx')
        send_file(root_path + f'Metis成交记录-{today_date}.xlsx')
        send_file(root_path + f'Leda成交记录-{today_date}.xlsx')
        break
    time.sleep(30)

# 20230608 增加股票数量校验
eur_buy = pd.read_excel(root_path + f'Europa成交记录-{today_date}.xlsx', sheet_name='累计卖出明细')
jup_buy = pd.read_excel(root_path + f'jupiter成交记录-{today_date}.xlsx', sheet_name='累计卖出明细')
sat_buy = pd.read_excel(root_path + f'saturn成交记录-{today_date}.xlsx', sheet_name='累计卖出明细')
metis_buy = pd.read_excel(root_path + f'Metis成交记录-{today_date}.xlsx', sheet_name='累计卖出明细')
leda_buy = pd.read_excel(root_path + f'Leda成交记录-{today_date}.xlsx', sheet_name='累计卖出明细')

eur_buy['买入日期'] = eur_buy['买入日期'].apply(lambda x: x.replace('-', ''))
jup_buy['买入日期'] = jup_buy['买入日期'].apply(lambda x: x.replace('-', ''))
sat_buy['买入日期'] = sat_buy['买入日期'].apply(lambda x: x.replace('-', ''))
metis_buy['买入日期'] = metis_buy['买入日期'].apply(lambda x: x.replace('-', ''))
leda_buy['买入日期'] = leda_buy['买入日期'].apply(lambda x: x.replace('-', ''))

right_buy = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/' + f'综合信息查询_成交回报_{today_date}.xls')
# right_buy_list = right_buy.query('委托方向 == "买入')['证券代码'].tolist()

# 20231012 新增小单测试剔除，买入100股为了作为测试单卖出用
right_buy_list = right_buy.query('委托方向 == "买入" & 持仓 != 100')['证券代码'].tolist()

eur_buy_list = eur_buy.query(f'买入日期 == "{today_date}"')['证券代码'].tolist()
jup_buy_list = jup_buy.query(f'买入日期 == "{today_date}"')['证券代码'].tolist()
sat_buy_list = sat_buy.query(f'买入日期 == "{today_date}"')['证券代码'].tolist()
metis_buy_list = metis_buy.query(f'买入日期 == "{today_date}"')['证券代码'].tolist()
leda_buy_list = leda_buy.query(f'买入日期 == "{today_date}"')['证券代码'].tolist()

today_record_list = list(set(set(eur_buy_list).union(set(jup_buy_list).union(sat_buy_list).union(set(metis_buy_list).union(set(leda_buy_list))))))
today_record_list = list(map(lambda x: int(x[:6]), today_record_list))

if set(today_record_list) == set(right_buy_list):
    print('True')
else:
    send_message(f'{today_date}成交记录与综合成交回报个股不对应')
    print(f'{today_date}成交记录与综合成交回报个股不对应')
    right_record = list(set(right_buy_list).difference(set(today_record_list)))
    record_right = list(set(today_record_list).difference(set(right_buy_list)))
    send_message('成交回报多了：' + ','.join(list(map(str, right_record))))
    send_message('成交回报少了：' + ','.join(list(map(str, record_right))))




